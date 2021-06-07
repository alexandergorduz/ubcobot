import page_parser

class CommercialOffer:
    def __init__(self):
        self.cards = []
        self.card_number = 0
        self.work_cost = 0

    def add_card(self, message):
        url, card_amount = page_parser.parse_input(message)
        html = page_parser.get_html(url)
        card = page_parser.get_page_content(html.text)
        self.card_number += 1
        self.cards.append(
            {
                'card_number': self.card_number,
                'card_image': card['card_image'],
                'card_url': url,
                'card_name': card['card_name'],
                'card_amount': card_amount,
                'card_price': card['card_price']
            }
        )