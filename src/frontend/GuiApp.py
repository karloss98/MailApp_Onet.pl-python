import tkinter
from tkinter import *
from src.backend import MailService
from functools import partial
from tkinter import ttk
import math
from tkinter import messagebox

height = 400
width = 400
geometry = str(width)+'x'+str(height)
color_entries_bg = 'pink4'
color_entries_fg = '#360a07'
color_labels_bg = '#ed837b'
color_labels_fg = '#360a07'
success_color_bg = '#2db00c'
color_main_frame = '#bd4e46'


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.login_frame = Frame(self.master, bg=color_main_frame, relief=RIDGE, bd=5)
        self.login_frame.pack(fill='both', expand=True)

        self.login_frame.pack(fill='both')
        self.login_frame.pack(expand=True)

        self.label_mail = Label(self.login_frame, font=('Arial', 14), text='Enter your email', bg=color_labels_bg, fg=color_labels_fg)
        self.label_mail.pack(pady=5, )

        self.entry_mail = Entry(self.login_frame, font=('Arial', 12), width=20, bg=color_entries_bg, bd=5, fg=color_entries_fg)
        self.entry_mail.pack(pady=5)

        self.label_password = Label(self.login_frame, font=('Arial', 14), text='Enter your password', bg=color_labels_bg)
        self.label_password.pack(pady=5)

        self.entry_password = Entry(self.login_frame, font=('Arial', 12), width=20, bd=5, bg=color_entries_bg, fg=color_entries_fg, show='*')
        self.entry_password.pack(pady=5)

        self.login_button = Button(self.login_frame, text='LOGIN', command=self.login)
        self.login_button.pack(side=TOP, pady=5)

        self.testlabel = Label(self.login_frame, text='bad credentials\ntry again')

    def login(self):
        active_email = self.entry_mail.get()
        password = self.entry_password.get()
        is_logged_in = MailService.login(active_email, password)
        global active_user
        active_user = active_email

        if is_logged_in:
            print('logged in')
            self.success_label = Label(self.login_frame,  bg=success_color_bg, fg=color_labels_fg)
            self.success_label.pack()
            self.load_new(active_user)

        else:
            print('bad credentials')
            self.testlabel.pack()

            MailService.session.close()
            # MailService.logout()

    def load_new(self, active_user):
        self.login_frame.destroy()
        SuccessPage(self.master, active_user)


class SuccessPage:
    def __init__(self, master, activeuser):

        MailService.get_foldersid_from_api()
        self.master = master

        self.frame = Frame(self.master, bg=color_main_frame, )
        self.frame.pack(expand=1, fill=BOTH)
        self.main_header = Frame(self.frame, bg=color_labels_bg, )
        self.main_header.place(x=0, y=0, width=360, height=20)

        button = Button(self.main_header, text='logged as: {}'.format(activeuser),)
        button.pack(side=RIGHT)

        logout_button = Button(self.main_header, text='logout', command=self.logout)
        logout_button.pack(side=LEFT)

        options = ['writemail', ]
        for i,v in MailService.foldersId.items():
            print(i)
            options.append(i)

        print(options)
        self.default_value = tkinter.StringVar()
        self.default_value.set(options[0])
        global active_folder
        active_folder = options[0]

        menu = OptionMenu(self.main_header, self.default_value, *options, command=self.load_another)
        self.previous_choice=self.default_value.get()
        menu.pack()
        root.title('Account')

        self.framemail = Frame(self.frame, bg='green')
        self.framemail.place(x=0, y=20, width=360, height=360)
        WriteMail(self.framemail, )

    def load_another(self, *args):
        choice = self.default_value.get()
        print(choice)


        if self.previous_choice==choice:
            print('to co wczesniej')
        else:
            self.framemail.destroy()
            self.framemail = Frame(self.frame, bg='green')
            self.framemail.place(x=0, y=20, width=400, height=400)

            self.previous_choice=choice

            if choice=='writemail':
                print('jestes w pisaniu')
                WriteMail(self.framemail)

            else:
                print('jestes w skrzynce')
                LoadInbox(self.framemail, choice)

    def logout(self):
        MailService.logout()
        self.frame.destroy()
        LoginWindow(root)
        active_user = ''


class WriteMail:
    def __init__(self, master, receiver=None, title=None):
        self.master = master
        receiver_label = Label(self.master, text='enter receiver')
        receiver_label.place(x=10, y=10, )

        self.enter_receiver = Entry(self.master, )
        self.enter_receiver.place(x=10, y=40)
        print(receiver)
        # self.enter_receiver.set
        if receiver!=None:
            self.enter_receiver.insert(1, receiver)



        title_label = Label(self.master, text='title of mail')
        title_label.place(x=200, y=10)

        self.title_entry = Entry(self.master,)
        self.title_entry.place(x=200, y=40)

        if title!=None:
            self.title_entry.insert(1, 're: {}'.format(title))

        mail_content_label = Label(self.master, text='write your mail')
        mail_content_label.place(x=10, y=70,)

        self.window_for_mail = Text(self.master, font=('Arial',12))
        self.window_for_mail.place(x=10, y=100, width=340, height=200)

        send_button = Button(self.master, text='send mail', command=self.send_mail)
        send_button.place(x=10, y=310)

    def send_mail(self, ):
        receiver = self.enter_receiver.get()
        title = self.title_entry.get()
        content = self.window_for_mail.get('1.0', END)
        print(active_user)
        MailService.send_mail_by_session(receiver, title, content, active_user)


class LoadInbox:

    def __init__(self, master, choice):
        # global choice
        self.choice = choice
        self.master = master
        # data = MailService.getJsonMails()

        self.inbox_label = Frame(self.master, bg='white', relief=SUNKEN, bd=5)
        self.inbox_label.place(x=0,y=0, width=360, height=350, )

        self.mail_content_box = Frame(self.inbox_label, bg='red')
        self.mail_content_box.place(x=0,y=0, height=220, width=350)

        self.loadContentOfBox(1, MailService.foldersId[choice])

        self.active_page = 1

        amount_of_mails = MailService.getFoldersInfo()[choice]

        self.button_frame = Frame(self.inbox_label, bg='red')
        self.button_frame.place(x=0, y=250, width=350, height=50)

        canvas_for_buttons = Canvas(self.button_frame, bg='yellow')
        canvas_for_buttons.pack(side=TOP, fill=BOTH, expand=1)

        scroll_to_buttons = ttk.Scrollbar(canvas_for_buttons, orient=HORIZONTAL, command=canvas_for_buttons.xview)
        scroll_to_buttons.pack(side=BOTTOM, fill=BOTH)

        canvas_for_buttons.configure(xscrollcommand=scroll_to_buttons.set)
        canvas_for_buttons.bind('<Configure>', lambda e: canvas_for_buttons.configure(scrollregion=canvas_for_buttons.bbox('all')))

        second_frame = Frame(canvas_for_buttons, bg='pink')

        canvas_for_buttons.create_window((0, 0), window=second_frame, anchor='nw')

        page_buttons = []
        w = 0
        # scroll = Scrollbar(self.button_frame, orient=tkinter.HORIZONTAL, )
        # scroll.pack(side=BOTTOM)

        # -----------add button to frame----------
        for i in range(0,math.ceil(amount_of_mails/10)):
            page_buttons.append(Button(second_frame,text=i+1, command=partial(self.change_page, i+1, choice)))
            page_buttons[i].grid(row=0, column=i)
            w += 20

    def change_page(self, page, choice):
        print(page)
        if self.active_page == page:
            print('do nothing because you pushed the same no. page')
        else:
            for widget in self.mail_content_box.winfo_children():
                widget.destroy()
            self.loadContentOfBox(page, MailService.foldersId[choice])
            self.active_page = page

    def loadContentOfBox(self, page, folderId):

        data = MailService.getJsonMails(page, folderId)

        self.delete_buttons = []
        self.display_buttons = []
        self.labels = []
        h = 0
        for i, v in enumerate(data):
            self.labels.append(Label(self.mail_content_box, text=data[i]['subject'], bg='white', relief=SUNKEN, bd=1, anchor='w'))
            # label1.pack(side=LEFT)
            self.labels[i].place(x=0, y=h, height=20, width=350, relx=0)
            self.delete_buttons.append(Button(self.labels[i], text='delete'.format(i + 1),
                                              command=partial(self.delete_mail, data[i], i, self.choice))) # ['mid']
            # you can use also expression: lambda i=i: self.print_mail_id(i)
            Button(self.labels[i], text='disp', command=partial(self.dispay,data[i], i)).pack(side=RIGHT)
            self.delete_buttons[i].pack(side=RIGHT)
            h += 20

        if folderId == MailService.foldersId['trash']:
            Button(self.mail_content_box, text='empty rubbish', command=MailService.emptyRubbishBin ).place(y=200)
            # Button.place(x=10, y=180)

        else:
            Button(self.mail_content_box, text='make it clean', command=partial(MailService.scanFolderForUnwantedEmails, folderId)).place(y=200)




    def dispay(self, i, v):
        print(i['mid'], )
        id = i['mid']
        from_sender, title, content = MailService.getSingleMail(id)
        print('from', from_sender)
        print('title', title)
        print('content', content)
        # test = content.replace(' ', '')
        # test=content.replace('\n', '')
        # test=content.replace('  ', '')
        # print('type contentu: ', type(test))
        
        self.display_mail = Frame(self.master, bg ='pink') #b7bdc7
        self.display_mail.place(x=10, y=80, width = 340, height=250)
        close_button = Button(self.display_mail, text='X', command = self.display_mail.destroy)
        close_button.pack(anchor='ne')

        resend_button = Button(self.display_mail, text='reply', command=partial(self.load_resend_frame, from_sender, title))#command=self.load_resend_frame(from_sender)) # WriteMail(self.master, from_sender)
        resend_button.place(x=200, y=0, )


        label_sender = Label(self.display_mail, )
        label_sender.place(anchor='nw',)

        label_sender.config(text=' from: {}'.format(from_sender))
        label_title_of_mail = Label(self.display_mail, text='title: {}'.format(title))
        label_title_of_mail.pack()

        content_text = Text(self.display_mail, )
        content_text.insert(tkinter.END, content)
        content_text.place(x=10, y=50, height=190, width=320)



    def load_resend_frame(self, receiver, title):
        for widget in self.inbox_label.winfo_children():
            widget.destroy()

        self.display_mail.destroy()
        self.inbox_label.destroy()
        WriteMail(self.master, receiver, title)

    def delete_mail(self, *args):
        print(args[0], args[1])
        to_delete = messagebox.askokcancel(message="do you want to delete this message?")
        email_to_delete = []
        email_to_delete.append(args[0]['mid'])
        print(email_to_delete)
        print(args[0]['mid'])

        print(to_delete)
        if to_delete:
            MailService.moveToRubbishBin(args[2],email_to_delete )
            pass
        # self.labels[args[1]].destroy()


def init_():
    global root
    root = Tk()
    root.geometry(geometry)
    root.config(bd=20, bg='#9c1006')
    root.title('Login to onet.pl')
    root.resizable(height=False, width=False)
    LoginWindow(root)
    root.mainloop()
