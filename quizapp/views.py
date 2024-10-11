from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import QuizAttempt
import torch
from PIL import Image
import io
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages

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
        img_file = request.FILES['image']
        img = Image.open(img_file)

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
        if "keyboard" in detected_classes:  # Adjust to match the correct label
            return redirect('question_two')

        return render(request, 'question_one.html', {'error': 'Please upload a picture of a keyboard!'})

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
