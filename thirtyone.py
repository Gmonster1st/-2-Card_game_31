# 31 1/18
"""
απλοποιημένη έκδοση του 31. Παίζουν 2-8 παίκτες, ο καθένας τραβάει διαδοχικά 'φύλλα'. Στόχος είναι
να πετύχει όσο το δυνατόν υψηλότερο συνολικό σκορ. Αν το συνολικό του σκορ περάσει όμως το 31 καίγεται.
Κερδίζει ο παίκτης ή οι παίκτες που έχουν το υψηλότερο σκορ σε κάθε γύρο
"""
# import random
import PlayingCards as pc


class Player:
    """κλάση που υλοποιεί τη συμπεριφορά του παίκτη του 31"""
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.score = 0

    def plays(self):
        card = self.deck.draw()
        print('Ο παίκτης {} τράβηξε: {}'.format(self.name, card.detailed_info()))
        card_value = self._calculate_value(card)
        self.score += card_value
        self._check_if_exceeded()
        if self.score != -1:
            reply = input('Το σκόρ είναι: {}. Θέλεις να ξαναπαίξεις (ν/ο);'.format(self.score))
            if not reply or reply.lower() not in "οo":
                self.plays()  # η συνάρτηση καλεί ξανά τον εαυτό της αν επιτρέπεται και ο παίκτης επιθυμεί να συνεχίσει
            else :
                print(self)
        else:
            print(self)

    def _check_if_exceeded(self):
        if self.score > 31:
            print('Δυστυχώς κάηκε ο {} :-('.format(self.name))
            self.score = -1

    def _calculate_value(self, card):
        ace_count = 0
        if card.value.isdigit(): return int(card.value)
        elif card.value == 'A':
            if self.score <= 20 and ace_count < 1:
                ace_count += 1
                return 11
            else: return 1  # TODO να χειρίζεται τον άσσο με ιδιαίτερο τρόπο OK
        else: return 10  # αφορά τις τιμές T,J,Q,K

    def __str__(self):
        return 'Ο Παίκτης '+self.name+' έχει:'+str(self.score)+' πόντους'


class ComputerPlayer(Player):
    """παίκτης που τραβάει μόνος του φύλλα, έχει στρατηγική"""
    def plays(self):
        card = self.deck.draw() # ο παίκτης τραβάει φύλλο
        print('Ο υπολογιστής ({}) τράβηξε: {}'.format(self.name, card.detailed_info()))
        card_value = self._calculate_value(card)
        self.score += card_value
        self._check_if_exceeded()
        if self._computer_strategy(): self.plays()
        else:
            print('ΥΠΟΛΟΓΙΣΤΗΣ:', self)

    def _computer_strategy(self):
        return False if self.score >= 25 or self.score == -1 else True


class Game():
    """κλάση που ξεκινάει το παιχνίδι, καλεί τους παίκτες να παίξουν και ανακηρύσσει το νικητή"""
    def __init__(self):
        print("Παίζουμε τριάντα-μία")
        self.n_players = self.number_of_players() # αποφάσισε πόσοι παίκτες παίζουν
        self.players = []  # λίστα με παίκτες
        self.d = pc.Deck()
        self.d.shuffle()
        char = ord('Α')
        for i in range(char, char+self.n_players):
            if chr(i) == 'Α': self.players.append(ComputerPlayer(chr(i), self.d)) # ο υπολογιστής είναι ο Α
            else: self.players.append(Player(chr(i), self.d))  # οι παίκτες έχουν ονόματα Β,Γ ..
        self.show_players()  # τύπωσε τους παίκτες
        self.play_game()

    def number_of_players(self):  # ζητάει από τον χρήστη τον αριθμό παικτών
        num = 0
        while num < 2 or num > 8:
            reply = input('Αριθμός παικτών (2-8)')
            if reply.isdigit() and 2 <= int(reply) <= 8:
                return int(reply)

    def play_game(self):  # καλεί διαδοχικά τους παίκτες να παίξουν και αποφασίζει ποιος νίκησε
        for p in self.players:
            print(50*'*', '\nΠαίζει ο παίκτης...', p.name)
            p.plays()
        self.show_winner()

    def show_winner(self):  # αποφασίζει ποιος είναι ο νικητής
        max_score = max(x.score for x in self.players)
        if max_score == -1: print("Δεν υπάρχει νικητής")
        else:
            winners = [x for x in self.players if x.score == max_score]
            print(50*'*', "\nΝικητής είναι : ")
            for player in winners:
                print(player)

    def show_players(self):  # μας τυπώνει τους παίκτες
        print('Παίκτες: [', end ='')
        for player in sorted(self.players, key=lambda x: x.name):
            print(player.name, end=',')
        print(']')
# ---


if __name__ == '__main__': Game()
