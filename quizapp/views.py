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

questions = [
    {"type": "image", "text": "Upload an image containing a person", "correct_label": "person"},
    {"type": "image", "text": "Upload an image containing a car", "correct_label": "car"},
    {"type": "text", "text": "What percentage of the brain is water?", "correct_answer": "90%"},
    {"type": "text", "text": "What is the largest mammal on Earth?", "correct_answer": "blue whale"},
    {"type": "text", "text": "How many continents are there?", "correct_answer": "7"},
]

def quiz_view(request,question_id):
    # Define your questions
    question = Question.objects.filter(id=question_id).first()
    print(question)
    questions = [
        {"type": "image", "text": question.text, "correct_label": question.correct_answer},
        {"type": "text", "text": question.statistic_question, "correct_answer": question.statistic_correct_answer},
    ]
    
    # Check if the user is on question 1 or question 2
    step = request.session.get('quiz_step'+str(question_id), 1)
    
    # Select the current question based on the step
    question = questions[step - 1]  # Access the question based on the current step

    # Handle POST request (answer submission)
    if request.method == 'POST':
        if question['type'] == 'image':
            img_data = request.POST.get('image')

            if not img_data:
                return render(request, 'quiz_template.html', {'error': 'No image data found!', 'question': question})

            try:
                header, encoded = img_data.split(',', 1)
                img = Image.open(BytesIO(base64.b64decode(encoded)))
            except (ValueError, base64.binascii.Error, IOError):
                return render(request, 'quiz_template.html', {'error': 'Invalid image data!', 'question': question})

            # Run YOLO model on the image
            img = img.convert("RGB")
            results = model(img)
            labels = results.xyxyn[0][:, -1].cpu().numpy()
            detected_classes = [model.names[int(label)] for label in labels]
            print("Detected Classes:", detected_classes)

            # Check if the correct object is detected
            if question['correct_label'] in detected_classes:
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.points += 10
                user_profile.save()
                messages.success(request, 'Correct! You earned 10 points.')
                
                # Move to the next question (sub-question)
                request.session['quiz_step'+str(question_id)] = 2
                return redirect('quiz_template',question_id=question_id)  # Reload quiz_view to get the next question
            else:
                return render(request, 'quiz_template.html', {'error': 'Wrong Answer!', 'question': question})

        elif question['type'] == 'text':
            answer = request.POST.get('answer')
            if int(answer) == question['correct_answer']:
                QuizAttempt.objects.create(user=request.user, question=Question.objects.filter(id=question_id).first(), score=10, answer=answer)
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.points += 10
                user_profile.save()
                messages.success(request, 'Correct! You earned 10 points.')

                # End the quiz after the last question
                request.session['quiz_step'+str(question_id)] = 1  # Reset for the next attempt if needed
                return redirect('welcome')  # Redirect to the welcome page or a success page
            else:
                return render(request, 'question_two.html', {'error': 'Incorrect answer, please try again.', 'question': question})

    # GET request (load the question)
    if question['type']=='text':
        return render(request, 'question_two.html', {
            'question_text': question['text'],  # Pass the question text
            'error': None  # Or any error message
        })
    elif question['type']=='image':
        return render(request, 'quiz_template.html', {
            'question_text': question['text'],  # Pass the question text
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

