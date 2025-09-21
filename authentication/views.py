from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileForm, CustomPasswordChangeForm




def register(request):
    """
    User registration view.
    Handles GET (show form) and POST (process registration) requests.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            
            
            # Log the user in automatically after registration
            login(request, user)
            
            # Add success message
            messages.success(
                request, 
                f'Welcome {user.first_name}! Your account has been created successfully.'
            )
            
            # Redirect to home page
            return redirect('home')
        else:
            # Add error message if form is not valid
            messages.error(
                request, 
                'Please correct the errors below.'
            )
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """
    User profile view for displaying and editing user information.
    Requires authentication.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user, user=request.user)
    
    return render(request, 'registration/profile.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    """
    Custom password change view with custom form and success handling.
    """
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)