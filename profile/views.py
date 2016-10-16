import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.shortcuts import render_to_response, render


# Create your views here.
from django.template import RequestContext

from library.log import rbe_logger
from library.mail.InvitationMail import InvitationEmail
from profile.forms import InviteForm
from profile.models import InvitationKey, UserProfile


@login_required
def profile(request, user_id):
    rc = RequestContext(request)
    # TODO differe between foreign and other profile in waht is given to the tempalte in the first palce
    if user_id:
        uf = User.objects.filter(id=user_id)
        if uf.exists():
            uf = uf.first()
        else:
            return render_to_response('profile.html', rc)
    else:
        uf = request.user

    p = UserProfile.objects.get(user=uf)
    rc['profile'] = p
    rc['invited_users'] = UserProfile.objects.filter(invited_by=uf)
    rc['invitation_keys'] = InvitationKey.objects.filter(user=request.user)
    return render_to_response('profile.html', rc)


@login_required
def overview(request):
    rc = RequestContext(request)
    rc['profiles'] = UserProfile.objects.all()
    return render_to_response('overview.html', rc)


@login_required
def aboutme(request):
    new_about_me = request.POST.get('new_about_me')

    if len(new_about_me) > 3000:
        return JsonResponse({'success': False, 'reason': "Sorry! Not more than 3000 characters allowed!"})

    prof = UserProfile.objects.get(user=request.user)
    prof.about_me_text = new_about_me
    prof.save()

    return JsonResponse({'success': True})


@login_required
def avatar_upload(request):
    print request.FILES

    file = request.FILES[u'0']
    ending = file.name.split('.')[-1]

    if ending not in ['png', 'jpg', 'jpeg']:
        return JsonResponse({'success': False, 'reason': "Unsupported file ending! allowed is png and jpeg!"})

    random_uuid = str(uuid.uuid4())
    prefix = ''

    if settings.DEBUG:
        prefix = '/core'

    static_path_part = '/static/tmp/img/{}.{}'.format(random_uuid, ending)
    default_storage.save(settings.BASE_DIR + prefix + static_path_part, ContentFile(file.read()))

    prof = UserProfile.objects.get(user=request.user)
    prof.avatar_link = static_path_part
    prof.save()

    return JsonResponse({'success': True, 'path': static_path_part})


@login_required
def invite(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InviteForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #TODO - restrict double invites across the whole network
            registration_key = form.save(commit=False)
            registration_key.user = request.user
            registration_key.key = str(uuid.uuid4()).replace('-', '')
            registration_key.save()

            try:
                ie = InvitationEmail()
                ie.send(recipient_list=[registration_key.email], username=request.user.username, key=registration_key.key)
                return render(request, 'invite.html', {})
            except Exception as e:
                rbe_logger.error("Could not send invite email to {}".format(registration_key.email))
                rbe_logger.exception(e)
                form.add_error(None, 'Could not send invite email. Technical Error.')
    else:
        form = InviteForm()

    return render(request, 'invite.html', {'form': form})


@login_required
def revoke(request, revoke_id):
    rk = InvitationKey.objects.filter(id=revoke_id, user=request.user)
    rk.delete()
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': request.user.id}))


