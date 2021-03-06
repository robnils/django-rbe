from django.shortcuts import render_to_response

from library.mail.GoogleEmailCommand import GoogleEmail


class WelcomeMail(GoogleEmail):

    required_fields = ['recipient_list', 'username']

    @property
    def subject(self):
        return '[RBE Network] Welcome'

    def body(self, variables):
        return render_to_response('emails/welcome_mail.html', variables).content