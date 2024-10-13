from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import QuizAttempt,UserProfile,Question
import torch
from PIL import Image
import io
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from io import BytesIO
import base64
from .forms import RegisterForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import random

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('welcome')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def welcome_view(request):
    questions=Question.objects.all()
    return render(request, 'welcome.html',{'questions':questions})
def success_view(request):
    return render(request,'success.html')
questions = [
    {"type": "image", "text": "Upload an image containing a person", "correct_label": "person"},
    {"type": "image", "text": "Upload an image containing a car", "correct_label": "car"},
    {"type": "text", "text": "What percentage of the brain is water?", "correct_answer": "90%"},
    {"type": "text", "text": "What is the largest mammal on Earth?", "correct_answer": "blue whale"},
    {"type": "text", "text": "How many continents are there?", "correct_answer": "7"},
]

def quiz_view(request, question_id):
    # Fetch the question object once
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return render(request, 'error_page.html', {'error': 'Question not found!'})

    # Define the questions
    questions = [
        {"type": "image", "text": question.text, "correct_label": question.correct_answer},
        {"type": "text", "text": question.statistic_question, "correct_answer": question.statistic_correct_answer},
    ]
    
    # Track the quiz step (1 or 2) for the question
    session_key = f'quiz_step{question_id}'
    step = request.session.get(session_key, 1)
    
    # Select the current question based on the step
    current_question = questions[step - 1]

    # Check if the user has already answered this question correctly
  # Redirect to the welcome page or another page of your choice
    if QuizAttempt.objects.filter(user=request.user, question=question).count()>=2:
        messages.info(request, 'You have already completed this question.')
        return redirect('welcome')
    # Handle POST request (answer submission)
    if request.method == 'POST':
        if current_question['type'] == 'image':
            img_data = request.POST.get('image')

            if not img_data:
                return render(request, 'quiz_template.html', {'error': 'No image data found!', 'question': current_question})

            try:
                header, encoded = img_data.split(',', 1)
                img = Image.open(BytesIO(base64.b64decode(encoded)))
            except (ValueError, base64.binascii.Error, IOError):
                return render(request, 'quiz_template.html', {'error': 'Invalid image data!', 'question': current_question})

            # Run YOLO model on the image
            img = img.convert("RGB")
            results = model(img)
            labels = results.xyxyn[0][:, -1].cpu().numpy()
            detected_classes = [model.names[int(label)] for label in labels]
            print("Detected Classes:", detected_classes)

            # Check if the correct object is detected
            if current_question['correct_label'].islower() in detected_classes:
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.total_score += 10
                user_profile.save()
                QuizAttempt.objects.create(user=request.user, question=question, score=10, answer='Image Answer')
                messages.success(request, 'Correct! You earned 10 points.')
                
                # Move to the next question (sub-question)
                request.session[session_key] = 2
                return redirect('quiz_template', question_id=question_id)  # Reload quiz_view to get the next question
            else:
                return render(request, 'quiz_template.html', {'error': 'Wrong Answer!', 'question': current_question})

        elif current_question['type'] == 'text':
            predicted = request.POST.get('answer')
            #predicted = request.POST.get('predicted')
            
            if predicted.isdigit():
                predicted = int(predicted)
                actual = question.statistic_correct_answer

                # Calculate score using the formula: 100 - |actual - predicted|
                score = 100 - abs(actual - predicted)

                # Create the quiz attempt and save the score
                QuizAttempt.objects.create(
                    user=request.user,
                    question=question,
                    score=score,
                    actual=actual,
                    predicted=predicted
                )
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.total_score += score
                user_profile.save()
                messages.success(request, 'Correct! You earned points.')
                #messages.success(request, 'Correct! You earned 10 points.')

                # End the quiz after the last question
                request.session[session_key] = 1  # Reset for the next attempt if needed
                return redirect('success')  # Redirect to the welcome page or a success page
            else:
                return render(request, 'question_two.html', {'error': 'Incorrect answer, please try again.', 'question': current_question})

    # GET request (load the question)
    if current_question['type'] == 'text':
        return render(request, 'question_two.html', {
            'question_text': current_question['text'],  # Pass the question text
            'error': None  # Or any error message
        })
    elif current_question['type'] == 'image':
        return render(request, 'quiz_template.html', {
            'question_text': current_question['text'],  # Pass the question text
            'error': None  # Or any error message
        })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the user to the database
            username = form.cleaned_data.get('username')
            #UserProfile.objects.create()
            #UserProfile.objects.save()
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})