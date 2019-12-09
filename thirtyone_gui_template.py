# 31gui 3/18
"""
απλοποιημένη έκδοση του 31. Παίζουν 2 o υπολογιστής και ο παίκτης. Ο υπολογιστής παίζει πρώτος., ο κάθε παίκτης
τραβάει διαδοχικά 'φύλλα'. Στόχος είναι να πετύχει όσο το δυνατόν υψηλότερο συνολικό σκορ. Αν το συνολικό του σκορ
περάσει όμως το 31 καίγεται.
Κερδίζει ο παίκτης που έχει το υψηλότερο σκορ σε κάθε γύρο
"""

"""
                                            ***ΣΗΜΕΙΩΣΗ***
        ΣΤΟΝ ΚΩΔΙΚΑ ΕΧΟΥΝ ΓΙΝΕΙ ΠΟΛΛΕΣ ΑΛΛΑΓΕΣ ΜΕ ΒΑΣΗ ΤΗΝ ΚΑΛΥΤΕΡΗ ΚΑΙ ΠΙΟ ΑΚΡΙΒΗΣ ΕΜΠΕΙΡΙΑ ΠΡΟΣ ΤΟ ΧΡΗΣΤΗ
                Ο ΚΩΔΙΚΑΣ ΠΟΥ ΕΧΕΙ ΑΛΛΑΧΤΕΙ ΒΡΙΣΚΕΤΑΙ ΑΝΑΜΕΣΑ ΑΠΟ ΣΗΜΕΙΩΣΕΙΣ ΜΕ ΑΣΤΕΡΑΚΙΑ
                
                                    ΕΛΠΙΖΩ ΝΑ ΑΠΟΛΑΥΣΕΤΕ ΤΟ ΠΑΙΧΝΙΔΙ
"""
import PlayingCards as pc
from thirtyone import Player, Game  # εισάγουμε τις κλάσεις Player, Game από την αρχική έκδοση του παιχνιδιού
import tkinter as tk
import os
from tkinter import simpledialog
import pickle
import random


class GUICard:
    """κλάση που γνωρίζει και τη γραφική ταυτότητα της card"""
    theCards = {}

    def __init__(self, card, canvas):
        self.canvas = canvas
        self.value = card.value
        self.symbol = card.symbol
        self.position = None
        self.image = None
        GUICard.theCards[card] = self

    def _fetch_image(self):
        if self.face:
            return CardImages.images[self.symbol][pc.Deck.values.index(self.value)]
        else: return CardImages.images['b']

    def _animate_image(self):
        self.canvas.move(self.image, self.img_vx, self.img_vy)
        x1, y1, x2, y2 = self.canvas.bbox(self.image)
        if abs(x1 - self.position[0]) < 5 and abs(y1 - self.position[1]) < 5:
            return
        else:
            self.canvas.update_idletasks()
            self.canvas.after(20, self._animate_image)

    def set_face(self, face):
        if self.position and face != self.face:
            self.face = face
            self.canvas.itemconfig(self.image, image=self._fetch_image())
        else:
            self.face = face

    def move_to(self, new_position):
        if not self.position: self.position = new_position
        if not self.image:
            self.image = self.canvas.create_image(*self.position, image=self._fetch_image())
        self.canvas.itemconfig(self.image, anchor='nw')
        if new_position != self.position:
            self.img_vx = (new_position[0] - self.position[0]) / 20
            self.img_vy = (new_position[1] - self.position[1]) / 20
            self._animate_image()
            self.position = new_position

    def __str__(self):
        out = self.value + self.symbol
        if self.position:
            out += '['+str(self.position[0])+','+str(self.position[1])+']'
        return out


class CardImages:
    """κλάση που δημιουργεί τις εικόνες των φύλλων από srpitesheet"""
    image_file = 'cards2.gif'
    path = '.'
    imagefile = os.path.join(path, image_file)
    images = {}
    @staticmethod
    def generate_card_images():
        # δημιουργία εικόνων των καρτών 79x123 px από το spritesheet cards2.gif
        num_sprites = 13
        place = 0
        spritesheet = tk.PhotoImage(file=CardImages.imagefile)
        for x in 'sdhc':
            CardImages.images[x] = [CardImages._subimage(79 * i, 0 + place,
                                                         79 * (i + 1), 123 + place,
                                                         spritesheet) for i in range(num_sprites)]
            place += 123
        CardImages.images['b'] = CardImages._subimage(0, place, 79, 123 + place, spritesheet)  # back image

    @staticmethod
    def _subimage(l, t, r, b, spritesheet):
        dst = tk.PhotoImage()
        dst.tk.call(dst, 'copy', spritesheet, '-from', l, t, r, b, '-to', 0, 0)
        return dst


class ComputerPlayer(Player):
    """κλάση που υλοποιεί τη συμπεριφορά του παίκτη"""
    def __init__(self, canvas, deck):
        self.canvas = canvas
        self.name = 'Big Blue'
        self.deck = deck
        self.score = 0
        self.hand = []  # τα χαρτιά του παίκτη
        self.start = GUI.padx, GUI.pady  # NW γωνία περιοχής για τις κάρτες του παίκτη
        self.next_card_position = self.place_of_next_card()
        self.message_place = self.start[0], round(self.start[1] + GUI.card_height * 1.1)
        self.infomessage = ""
        self.active = False

    def place_of_next_card(self):
        return self.start[0] + (GUI.card_width // 2) * len(self.hand), self.start[1]

    def receive(self, card):  # adds a new card to player
        self.hand.append(card)
        self.next_card_position = self.place_of_next_card()
        return len(self.hand) - 1

    def plays(self, face=False):
        if self.active:
            card = GUICard.theCards[self.deck.draw()]
            card.set_face(face)
            card.move_to(self.place_of_next_card())
            self.receive(card)
            card_value = self._calculate_value(card)
            self.score += card_value
            self._check_if_exceeded()
            if self._computer_strategy() and self.score != -1:
                root.after(1000, self.plays)
            else:
                self.show_cards()
                self.active = False
                if self.score == -1:
                    self.update_message()
                # ************************************************************************************************
                    app.stop()  # **Βελτίωση: Αν ο υπολογιστής καεί, τελειώνει το παιχνίδι με νικητή τον παίκτη**
                if self.score == 31: app.stop()  # Αν ο παίκτης έχει 31, ανακηρρύσεται αυτόματα νικητής
                # ************************************************************************************************

    def show_cards(self, all=False):
        if self.score == -1 or all:
            for card in self.hand:
                card.set_face(True)
        else:
            card_to_hide = random.randint(0, len(self.hand)-1)
            for i, card in enumerate(self.hand):
                if i != card_to_hide:
                    card.set_face(True)

    def _computer_strategy(self):
        return False if self.score >= 25 or self.score == -1 else True

    def update_message(self):
        # ************************************************************************************************
        # Ελέγχει το όνομα και διαμορφώνει το μήνυμα ανάλογα με το όνομα του παίκτη
        article_burn = self.name + ' έχει... ' + 'καεί'
        article_play = self.name + ' έχει... ' + str(self.score)
        if self.score == -1:
            self.infomessage = 'ο ' + article_burn if self.name[-1] in "sς" else 'η ' + article_burn
        else:
            self.infomessage = 'ο ' + article_play if self.name[-1] in "sς" else 'η ' + article_play
        self.canvas.itemconfig(self.my_message, text=self.infomessage, state='normal')
        # ************************************************************************************************
        # TODO Ερώτημα (β): ενημέρωση μηνύματος στην περιοχή του χρήστη OK

    # ************************************************************************************************
    # Δημιούργησα αυτήν τη μέθοδο διότι με τον τρόπο με τον οποίο το text δημιουργούνταν, δεν μου το εμφάνιζε στον canva
    # Με αυτήν τη λύση δημιουργείται 1 text για κάθε αντικείμενο computer και human... δείτε τα καλέσματα της μεθόδου
    # μέσα στη μέθοδο GUIGame.play_game()
    def create_message(self):
        self.my_message = self.canvas.create_text(*self.message_place,
                                                  fill="white", text=self.infomessage, font="Arial 30", anchor='nw')
        # ************************************************************************************************


class HumanPlayer(ComputerPlayer):
    """κλάση που εξειδικεύει τον παίκτη για την περίπτωση του χρήστη"""
    def __init__(self, *args, **kwds):
        ComputerPlayer.__init__(self, *args, **kwds)
        self.start = GUI.padx, GUI.board_height - GUI.pady - GUI.card_height  # περιοχή φύλλων χρήστη
        self.name = 'Παίκτης'
        self.message_place = self.start[0], round(self.start[1] - 0.6 * GUI.card_height)
        # TODO Ερώτημα (γ) να ζητείται το όνομα του χρήστη OK
        # ************************************************************************************************
        # Ελέγχει αν ο παίκτης έχει παίξει ξανά και αν όχι, ζητάει το όνομα
        if app.games_played == 0:
            # ---------------------------------------------------------------------------------
            # Ελέγχει αν το όνομα που έδωσε ο χρήστης είναι πάνω από 20 χαρακτήρες
            while True:
                self.name_input = simpledialog.askstring('Όνομα Παίκτη', prompt='Δώσε Όνομα Παίκτη')
                if self.name_input is not None and self.name_input != '':
                    max_char = self.name_input
                    if len(max_char) > 20:
                        tk.messagebox.showwarning('Προσοχή', 'Το όνομα πρέπει να έχει μέγιστο 20 χαρακτήρες!',
                                                  parent=root)
                        pass
                    else:
                        app.username = self.name_input
                        self.name = app.username
                        break
                else:
                    break
            # ---------------------------------------------------------------------------------
        else:
            self.name = app.username  # Αν δεν είναι νέος παίκτης κρατάει το ίδιο όνομα
        # ************************************************************************************************

    def plays(self, face=True):
        if self.active:
            card = GUICard.theCards[self.deck.draw()]
            card.set_face(face)
            card.move_to(self.place_of_next_card())
            self.receive(card)
            card_value = self._calculate_value(card)
            self.score += card_value
            self._check_if_exceeded()
            self.update_message()
            root.update_idletasks()
            if self.score == -1:
                self.active = False
                app.find_winner()
            # ************************************************************************************************
            if self.score == 31: app.stop()  # Αν ο παίκτης έχει 31 ανακηρρύσεται αυτόματα νικητής
            # ************************************************************************************************


class GUI:
    """κλάση με τις παραμέτρους του γραφικού περιβάλλοντος"""
    board_width, board_height = 900, 600  # διαστάσεις καμβά
    card_width, card_height = 79, 123  # διαστάσεις τραπουλόχαρτου
    padx, pady = 50, 50  # κενό μεταξύ του καμβά και ενεργού περιοχής
    deck = (800, 230)
    # περιοχή τράπουλας
    deck_of_cards_area = (deck[0], deck[1], deck[0] + card_width, deck[1] + card_height)
    @staticmethod
    def in_area(point, rect):
        if point[0] >= rect[0] and point[0] <= rect[2] and point[1] >= rect[1] and point[1] <= rect[3]:
            return True
        else:
            return False


class GUIGame(Game, GUI):
    """Κεντρικός ελεγκτής του παιχνιδιού, δημιουργεί επιφάνεια, δημιουργεί τους παίκτες"""
    def __init__(self, root):
        # --- Game parameters
        self.root = root
        root.title("Παιχνίδι 31gui - εκδ 1.2")
        root.resizable(width='false', height='false')
        # --- GUI parameters
        self.infomessage_position = GUI.padx, GUI.board_height // 2 - 22
        self.top_font = 'Arial 20'
        self.f = tk.Frame(root)
        self.f.pack(expand=True, fill='both')
        self.create_widgets()
        self.run = False
        self.winner = None
        self.username = None
        # ************************************************************************************************
        self.games_played = 0  # **Μετρητής παιχνιδιών**
        # ************************************************************************************************

    def create_widgets(self):
        # TODO Ερώτημα (α) δημιουργία πλήκτρου έναρξης νέου παιχνιδιού, πλήκτρου διακοπής 'αρκετά!', σκορ, OK
        # TODO πλήκτρο αποθήκευσης σκορ και πλήκτρο ανάκτησης των 5 καλύτερων σκορ OK
        # ************************************************************************************************
        # Δημιουργία Frame με 4 πλήκτρα
        self.f1 = tk.Frame(self.f, height=30)
        self.f1.pack(fill='both')
        self.b_new = tk.Button(self.f1, text="Νέο Παιχνίδι", width=15, relief='raise',
                               command=self.play_game)
        self.b_new.focus()  # Επιλέγει αυτόματα το κουμπί και ο χρήστης μπορεί να πατήσει spacebar για ενεργοποίηση
        self.b_new.pack(side='left', fill='y', padx=2, pady=2)
        self.b_save = tk.Button(self.f1, text="Αποθήκευση Σκορ", state="disabled", width=15, relief='raise',
                                command=self.save_score)
        self.b_save.pack(side='left', fill='y', padx=2, pady=2)
        self.b_about = tk.Button(self.f1, text="Περί", width=15, relief='raise',
                                 command=self.info)
        self.b_about.pack(side='left', fill='y', padx=2, pady=2)
        self.b_stop = tk.Button(self.f1, text="Αρκετά", state="disabled", width=15, relief='raise',
                                command=self.stop)
        self.b_stop.pack(side='left', fill='y', padx=2, pady=2)
        self.match_score = tk.Label(self.f1, width=33, font="Arial 16",
                                    text='Σκορ',
                                    relief='sunken')
        self.match_score.pack(side="right", expand='true', padx=2, pady=2)
        # ************************************************************************************************
        self.f2 = tk.Frame(self.f)
        self.f2.pack(fill='both')
        self.canvas = tk.Canvas(self.f2, width=self.board_width, height=self.board_height, bg='darkgreen')
        self.canvas.pack(side='left', fill='x', expand=1)
        self.canvas.bind("<Button-1>", self.board_event_handler)
        # o παρακάτω κώδικας να αντικατασταθεί από την απάντηση στο ερώτημα για το πλήκτρο 'αρκετά!!'
        # self.canvas.bind("<Button-2>", self.stop)
        # self.canvas.bind("<Button-3>", self.stop)
        self.message = ""
        self.score = [0, 0]
        self.canvas_info_message = ''
        # self.play_game()
        self.username = 'Παίκτης'
        # ************************************************************************************************
        self.filename = 'High_scores.db'
        # ************************************************************************************************

    def save_score(self):
        # ************************************************************************************************
        high_scores = []  # Φορτώνει τα δεδομένα του αρχείου, αν υπάρχει, προς επεξεργασία
        try:
            with open(self.filename, 'rb') as file:
                high_scores = pickle.load(file)
                file.close()
        except FileNotFoundError:
            pass
        except Exception as e:
            tk.messagebox.showinfo('Σφάλμα', e, parent=root)
        if self.games_played >= 3 and self.human.name != 'Παίκτης':  # Ελέγχει αν επιτρέπεται στο χρήστη να αποθηκεύσει
            save_score = self.computer.name + ' - ' + self.human.name + ' : ', self.score
            high_scores.append(save_score)
        try:
            with open(self.filename, 'wb') as file:
                pickle.dump(high_scores, file)
                file.close()
                self.b_save.config(state='disable')  # Αποτρέπει την πολλαπλή αποθήκευση ενός score
                # Ρωτάει τον παίκτη αφού έχει αποθηκευτεί το score του αν θέλει να συνεχίσει και
                # αν όχι μηδενίζει τα παιχνίδια και το score και περιμένει καινούριο παίκτη
                new_player = tk.messagebox.askyesno('Αποθήκευση Score', 'Το score σας έχει αποθηκευτεί!'
                                                                        '\nΘέλετε να συνεχίσετε;')
                if not new_player:
                    self.games_played = 0
                    self.score = [0, 0]
        except Exception as e:
            tk.messagebox.showinfo('Σφάλμα', e, parent=root)
        # ************************************************************************************************
        # TODO ερώτημα (δ) δυνατότητα αποθήκευσης σκορ OK

    def info(self):
        # ************************************************************************************************
        high_scores = []  # Λίστα που θα δεχτεί τα δεδομένα του αρχείου
        try:
            with open(self.filename, 'rb') as file:
                high_scores = pickle.load(file)
                file.close()
        except FileNotFoundError:
            tk.messagebox.showinfo('Αρχείο', 'Το αρχείο της βάσης δεν βρέθηκε!', parent=root)
            return
        except Exception as e:
            tk.messagebox.showinfo('Σφάλμα', e, parent=root)
        hall_of_fame = []  # Λίστα που δέχεται τα δεδομένα για την ταξινόμηση και εμφάνιση των καλύτερων 5 score
        # ---------------------------------------------------------------------------------
        # Επεξεργασία δεδομένων
        for i in high_scores:
            score = i[1]
            num1 = score[0]
            num2 = score[1]
            num_of_games = num1 + num2
            success = (num2 * 100)/num_of_games
            entry = i[0], success, num_of_games, num1, num2
            hall_of_fame.append(entry)
        # ---------------------------------------------------------------------------------
        # Ταξινόμηση με κριτήρια πρώτα το ποσοστό επιτυχίας και μετά τον αριθμό παιχνιδιών
        # Παράδειγμα: "Εάν τα παιχνίδια ειναι 10 και το ποσοστό επιτυχίας είναι 60%, η θέση θα είναι κάτω από κάποιον που
        # έχει >60% με λιγότερα παιχνίδια, αντίστροφα εάν ο το ποσοστό είναι =60% και τα παιχνίδια είναι 11,
        # η θέση θα είναι από πάνω"
        # Με την χρήση ανώνυμης μεθόδου x[1] = success και x[2] = num_of_games
        hall_of_fame.sort(key=lambda x: (x[1], x[2]), reverse=True)
        # ---------------------------------------------------------------------------------
        # Δημιουργία και μορφοποίηση κειμένου για το Toplevel παράθυρο
        score_board_names = ''
        score_board_scores = ''
        header = 'Τα 5 καλύτερα score!'
        for s in range(5):
            score_board_names += hall_of_fame[s][0] + '\n'
            score_board_scores += str(hall_of_fame[s][3]) + ' - ' + str(hall_of_fame[s][4]) + '\n'
        # ---------------------------------------------------------------------------------
        # Δημιουργία Toplevel παραθύρου για την εμφάνιση του Hall Of Fame
        wx = root.winfo_x()
        wy = root.winfo_y()
        pop_up = tk.Toplevel(root)
        pop_up.geometry('450x250+%d+%d' % ((wx + (GUI.board_width // 2)) - 165, (wy + (GUI.board_height // 2)) - 150))
        pop_up.focus_force()  # Θέτει το Toplevel παράθυρο σαν ενεργό
        pop_up.title("Hall Of Fame")
        pop_up.resizable(width='false', height='false')
        pop_up.grab_set()  # Αποτρέπει τη χρήση του κεντρικού παραθύρου μέχρι να κλείσει το Toplevel παράθυρο
        button = tk.Button(pop_up, text='OK', width=10, height=1, relief='raise',
                           command=lambda: pop_up.destroy(), anchor='s')
        button.focus()  # Επιλέγει αυτόματα το κουμπί και ο χρήστης μπορεί να πατήσει spacebar για ενεργοποίηση
        button.pack(side='bottom', padx=2, pady=2)
        tk.Label(pop_up, bg='lightyellow', text=header,
                 font=('Arial', 16, 'underline')).pack(fill='x', pady=(5, 0), padx=5)  # Υπογραμμισμένο κείμενο
        tk.Label(pop_up, bg='lightyellow', text=score_board_names, justify='left',
                 font=('Arial', 16)).pack(side='left', expand='true', fill='both', pady=(0, 5), padx=(5, 0))
        tk.Label(pop_up, bg='lightyellow', text=score_board_scores, justify='right',
                 font=('Arial', 16)).pack(side='left', expand='true', fill='both', pady=(0, 5), padx=(0, 5))
        # ************************************************************************************************
        # TODO ερώτημα (ε) δυνατότητα παρουσίασης υψηλότερων σκορ OK

    def play_game(self):
        self.deck = pc.Deck()
        self.deck.shuffle()
        self.computer = ComputerPlayer(self.canvas, self.deck)
        self.human = HumanPlayer(self.canvas, self.deck)
        self.username = self.human.name
        # ************************************************************************************************
        # Ενημέρωση του Label με το score των παικτών στην αρχή του παιχνιδιού
        # Αύξηση του μετρητή παιχνιδιών
        self.match_score.config(text=self.computer.name+': '+str(self.score[0])+' - '+self.human.name+': ' +
                                str(self.score[1]))
        self.games_played += 1
        # ************************************************************************************************
        self.canvas.delete('all')
        for card in self.deck.content:
            c = GUICard(card, self.canvas)
            c.set_face(False)
            c.move_to(GUI.deck)
        self.run = True
        # ************************************************************************************************
        # απενεργοποίηση πλήκτρου επανεκκίνησης
        self.b_new.config(state='disabled')
        '''
        Το πλήκτρο '...αρκετά!' ενεργοποιείται μέσα στην board_event_handle μόλις ο παίκτης τραβήξει το πρώτο φύλλο
        έτσι αποφεύγεται και η εμφάνιση διπλού αποτελέσματος σε περίπτωση που ο υπολογιστής καεί
        '''
        # ************************************************************************************************
        self.winner = None
        self.computer.active = True
        self.computer.create_message()  # ***Δημιουργία μηνύματος του Big Blue***
        self.human.create_message()  # ***Δημιουργία μηνύματος του Παίκτη***
        self.computer.plays()
        # human to play
        root.update_idletasks()
        if self.computer.score == -1:
            root.after_idle(self.stop_drawing_cards)
        else:
            root.after_idle(self.human_turn)

    def human_turn(self):
        self.human.active = True

    def board_event_handler(self, event):
        # ************************************************************************************************
        # Ενεργοποίηση του πλήκτρου '...αρκετά'
        if self.human.active and not self.computer.active:
            self.b_stop.config(state='normal')
            self.b_stop.focus()  # Επιλέγει αυτόματα το κουμπί και ο χρήστης μπορεί να πατήσει spacebar για ενεργοποίηση
        if self.run:  # Βελτίωση: Για να μην βγάζει σφάλμα αν πατήσεις κλικ στην περιοχή του canva πριν το νέο παιχνίδι
            # ********************************************************************************************
            x = event.x
            y = event.y
            # ************************************************************************************************
            # Βελτίωση: Πιο λεπτομερής έλεγχος ώστε να μην μπορεί ο παίκτης να ξεκινήσει να τραβάει πριν τελειώσει ο Η\Υ
            if self.human.active and not self.computer.active and self.human.score != -1:
                # ********************************************************************************************
                if GUI.in_area((x, y), GUI.deck_of_cards_area):
                    # Ο χρήστης έχει πατήσει στην περιοχή της τράπουλας
                    self.human.plays()

    def find_winner(self):  # αποφασίζει ποιος είναι ο νικητής
        max_score = max(self.computer.score, self.human.score)
        if max_score == -1:
            the_winner_is = 'Δεν υπάρχει νικητής'
            winner = False
        else:
            winner = 'human' if self.human.score == max_score else 'computer'
            the_winner_is = self.human.name if winner == 'human' else self.computer.name
            article = 'ο' if the_winner_is[-1] in "sς" else 'η'
            if winner == 'human' and len(self.human.name) > 10:
                the_winner_is = 'Νικητής είναι {} \n {} !!!'.format(article, the_winner_is)
            else:
                the_winner_is = 'Νικητής είναι {} {} !!!'.format(article, the_winner_is)
        if winner == 'human':
            self.score[1] += 1
        elif winner == 'computer':
            self.score[0] += 1
        self.computer.show_cards(all=True)
        self.computer.update_message()
        # ************************************************************************************************
        # Ενημέρωση του Label με το score των παικτών στο τέλος του παιχνιδιού
        self.match_score.config(text=self.computer.name + ': ' + str(self.score[0]) + ' - ' + self.human.name + ': ' +
                                str(self.score[1]))
        # ************************************************************************************************
        self.pop_up(the_winner_is)
        self.run = False
        self.winner = None
        # ************************************************************************************************
        # ενεργοποίησε πλήκτρο επανεκκίνησης, απενεργοποίησε πλήκτρο διακοπής
        self.b_new.config(state='normal')
        self.b_new.focus()  # Επιλέγει αυτόματα το κουμπί και ο χρήστης μπορεί να πατήσει spacebar για ενεργοποίηση
        self.b_stop.config(state='disabled')
        # Έλεγχος αν έχουν παιχτεί 3 παρτίδες και πάνω για την ενεργοποίηση του πλήκτρου αποθήκευσης score
        if self.games_played >= 3 and self.human.name != 'Παίκτης': self.b_save.config(state='normal')
        # ************************************************************************************************

    def pop_up(self, msg):
        # ************************************************************************************************
        # Δημιουργεί ένα Toplevel παράθυρο σε συγκεκριμένη θέση μπροστά απο το κεντρικό παράθυρο
        wx = root.winfo_x()
        wy = root.winfo_y()
        pop_up = tk.Toplevel(root)
        pop_up.geometry('250x100+%d+%d' % ((wx + (GUI.board_width//2)) - 70, (wy + (GUI.board_height//2)) - 10))
        pop_up.focus_force()  # Θέτει το Toplevel παράθυρο σαν ενεργό
        pop_up.title("Αποτέλεσμα")
        pop_up.resizable(width='false', height='false')
        pop_up.grab_set()  # Αποτρέπει τη χρήση του κεντρικού παραθύρου μέχρι να κλείσει το Toplevel παράθυρο
        tk.Label(pop_up, text=msg, height=3, width=50, font=('Arial', 13)).pack(pady=5, padx=5)
        button = tk.Button(pop_up, text='OK', width=10, height=1, relief='raise',
                           command=lambda: pop_up.destroy())
        button.focus()  # Επιλέγει αυτόματα το κουμπί και ο χρήστης μπορεί να πατήσει spacebar για ενεργοποίηση
        button.pack(padx=2, pady=2)
        # ************************************************************************************************
        #  TODO συντεταγμένες στο όριο του καμβά OK

    def stop(self):
        self.stop_drawing_cards()
        # ************************************************************************************************
        self.human.active = False  # Βάζει τον παίκτη ανενεργό για να μην μπορεί να τραβήξει ξανά
        # ************************************************************************************************

    def stop_drawing_cards(self):
        self.find_winner()
        self.canvas.update_idletasks()


if __name__ == '__main__':
    root = tk.Tk()
    CardImages.generate_card_images()
    app = GUIGame(root)
    root.mainloop()
