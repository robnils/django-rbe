from django.shortcuts import render_to_response

from library.mail.GoogleEmailCommand import GoogleEmail


class PasswordResetMail(GoogleEmail):

    required_fields = ['recipient_list', 'username', 'reset_key', 'valid_until']

    @property
    def subject(self):
        return '[RBE Network] Password reset'

    def body(self, variables):
        return render_to_response('emails/password_reset_mail.html', variables).content