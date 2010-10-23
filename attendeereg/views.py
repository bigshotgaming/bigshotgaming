from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from attendeereg.models import SignupForm

@login_required
def signup(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SignupForm(request.POST) # A form bound to the POST data
        print form.cleaned_data # All validation rules pass
        return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = SignupForm() # An unbound form

    return render_to_response('attendeereg/signup.html', {
        'form': form,
    })
