from src.backend import MailService
import pytest
from src.backend.MailService import login


class TestBackend:

    def test_LoginFailure(self):
        isLogged = login('karldawdawoss@onet.eu', 'korefaoeh7')
        assert isLogged==False

    def test_LoginSuccess(self):
        result = login('testkonto132@onet.pl', 'Aa123456')
        MailService.session.close()
        assert result == True

    def test_Session(self):
        login('testkonto132@onet.pl', 'Aa123456')
        print(MailService.session)
        MailService.session.close()
        print(MailService.session)
        MailService.logout()
        login('testkonto132@onet.pl', 'Aa123456')
        print(MailService.session)
        # MailService.session.




