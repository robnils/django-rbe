from django.shortcuts import render_to_response

from library.mail.GoogleEmailCommand import GoogleEmail


class TestEmail(GoogleEmail):

    @property
    def subject(self):
        return "This is a test email"

    def body(self, variables):
        variables.update({'about_missing': True, 'location_missing': True, 'username': 'hannes'})
        return render_to_response('emails/profile_completion.html', variables).content


