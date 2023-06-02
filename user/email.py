from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = 'p2p_user/activation.html'


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'p2p_user/password_reset.html'


class UserAccountDeleteEmail(email.BaseEmailMessage):
    template_name = 'p2p_user/delete_user_account.html'


class EmailResetEmail(email.UsernameResetEmail):
    template_name = 'p2p_user/email_reset.html'


class PhoneNumberConfirmEmail(email.BaseEmailMessage):
    template_name = 'p2p_user/phone_number_confirm.html'
