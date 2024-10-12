from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import QuizAttempt,UserProfile
import torch
from PIL import Image
import io
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from io import BytesIO
import base64

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
    return render(request, 'welcome.html')


@login_required
def question_one_view(request):
    if request.method == 'POST':
        img_data = request.POST.get('image')

        if not img_data:  # Check if img_data is None or empty
            return render(request, 'question_one.html', {'error': 'No image data found!'})

        try:
            header, encoded = img_data.split(',', 1)  # Attempt to split the data
            img = Image.open(BytesIO(base64.b64decode(encoded)))  # Decode the image
        except ValueError:
            return render(request, 'question_one.html', {'error': 'Invalid image data!'})

        # Convert image to YOLO compatible format
        img = img.convert("RGB")

        # Run YOLO model on the image
        results = model(img)

        # Extract labels detected
        labels = results.xyxyn[0][:, -1].cpu().numpy()

        # Print all labels detected for debugging
        detected_classes = [model.names[int(label)] for label in labels]
        print("Detected Classes:", detected_classes)

        # Check if "keyboard" is detected
        for i in detected_classes:
            if i=="person": # Adjust to match the correct label
                # Update user points in the database
                user_profile = UserProfile.objects.get(user=request.user)  # Get the user profile
                user_profile.points += 10  # Add 10 points
                user_profile.save()  # Save the updated profile

                return redirect('question_two')  # Redirect to the next question

        return render(request, 'question_one.html', {'error': 'Wrong Answer!'})

    return render(request, 'question_one.html')



@login_required
def question_two_view(request):
    if request.method == 'POST':
        answer = request.POST.get('answer')
        if answer == '90%':
            QuizAttempt.objects.create(user=request.user, question_number=2, score=10, answer=answer)
            return render(request, 'success.html', {'message': 'Correct! You have been awarded points.'})
        else:
            return render(request, 'question_two.html', {'error': 'Incorrect answer, please try again.'})
    return render(request, 'question_two.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, 'logout.html')
