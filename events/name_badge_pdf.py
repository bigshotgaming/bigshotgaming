from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.units import inch
from settings import STATIC_ROOT
import os

class NameBadgePDF:
    def __init__(self, filename, names):
        self.canvas = canvas.Canvas(filename, pagesize=letter)
        self.names = names
        
        self.font_name = 'Courier-Bold'
        self.header_text = 'BSG MegaLAN XVI'
        self.header_font_size = 16

        self.bottom_font_size = 28

        self.logo_image = os.path.join(STATIC_ROOT, 'images/events/namebadge_bg_alpha.jpg')
        self.logo_image_width = 155
        self.logo_image_height = 162

        self.name_y_placement_delta = 110
        self.name_size = 46

        self.doc_width, self.doc_height = letter
        self.margins = {
            'top' : 0.25 * inch,
            'bottom' : 0.25 * inch,
            'left' : 0.875 * inch,
            'right' : 0.875 * inch,
        }
        self.badge_height = (self.doc_height - self.margins['top'] - self.margins['bottom']) / 3
        self.badge_width = (self.doc_width - self.margins['right'] - self.margins['left']) / 3
        
        self.badge_locations = []
        for h in range(0, 3):
            for w in range(0, 3):
                self.badge_locations.append((self.margins['left'] + self.badge_width * w, self.doc_height - self.margins['top'] - self.badge_height * (h + 1)))

        self.draw_lines()
        self.location_number = 0
        
        for name, p_type in names:
            self.canvas.drawImage(self.logo_image, self.badge_locations[self.location_number][0] + (self.badge_width - self.logo_image_width) / 2, self.badge_locations[self.location_number][1] + 50, width=self.logo_image_width, height=self.logo_image_height)
    
            self.canvas.setFont(self.font_name, self.header_font_size)
            self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(self.header_text)) / 2), self.badge_locations[self.location_number][1] + self.badge_height - self.header_font_size - 7, self.header_text)

            self.canvas.setFont(self.font_name, self.bottom_font_size)
            self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(p_type)) / 2), self.badge_locations[self.location_number][1] + self.bottom_font_size - 10, p_type)
            
            self.set_biggest_name_size(name)
            
            if self.new_name_size < 14:
                if name.find(' ') != -1:
                    parts = name.split(' ')
                    line_one = ' '.join(parts[:(len(parts) / 2)])
                    line_two = ' '.join(parts[len(parts) / 2:])
                    
                    self.set_biggest_name_size(line_one)
                    font_size_1 = self.new_name_size
                    self.set_biggest_name_size(line_two)
                    font_size_2 = self.new_name_size
                    
                    if font_size_1 < font_size_2:
                        font_size = font_size_1
                    else:
                        font_size = font_size_2
                    
                    self.canvas.setFont(self.font_name, font_size)
                    self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(line_one)) / 2), self.badge_locations[self.location_number][1] + self.name_y_placement_delta + font_size, line_one)
                    self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(line_two)) / 2), self.badge_locations[self.location_number][1] + self.name_y_placement_delta, line_two)
                else:
                    self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(name)) / 2), self.badge_locations[self.location_number][1] + self.name_y_placement_delta, name)
            else:
                self.canvas.drawString(self.badge_locations[self.location_number][0] + ((self.badge_width - self.canvas.stringWidth(name)) / 2), self.badge_locations[self.location_number][1] + self.name_y_placement_delta, name)
            
            self.location_number += 1
            if self.location_number == len(self.badge_locations):
                self.canvas.showPage()
                self.draw_lines()
                self.location_number = 0
                
    def set_biggest_name_size(self, name):
        self.canvas.setFont(self.font_name, self.name_size)
        self.new_name_size = self.name_size
        while self.canvas.stringWidth(name) >= self.badge_width - 6:
            self.new_name_size -= 1
            self.canvas.setFont(self.font_name, self.new_name_size)
                
    def draw_lines(self):
        self.canvas.setDash(1,4)
        # top line
        self.canvas.line(self.margins['left'], self.doc_height - self.margins['top'], self.doc_width - self.margins['right'], self.doc_height - self.margins['top'])
        # bottom line
        self.canvas.line(self.margins['left'], self.margins['bottom'], self.doc_width - self.margins['right'], self.margins['bottom'])
        # left line
        self.canvas.line(self.margins['left'], self.doc_height - self.margins['top'], self.margins['left'], self.margins['bottom'])
        # right line
        self.canvas.line(self.doc_width - self.margins['right'], self.doc_height - self.margins['top'], self.doc_width - self.margins['right'], self.margins['bottom'])

        # horizontal lines
        self.canvas.line(self.margins['left'],self.doc_height - self.margins['top'] - self.badge_height, self.doc_width - self.margins['right'], self.doc_height - self.margins['top'] - self.badge_height)
        self.canvas.line(self.margins['left'],self.doc_height - self.margins['top'] - self.badge_height * 2, self.doc_width - self.margins['right'], self.doc_height - self.margins['top'] - self.badge_height * 2)

        # vertical lines
        self.canvas.line(self.margins['left'] + self.badge_width, self.doc_height - self.margins['top'], self.margins['left'] + self.badge_width, self.margins['bottom'])
        self.canvas.line(self.margins['left'] + self.badge_width * 2, self.doc_height - self.margins['top'], self.margins['left'] + self.badge_width * 2, self.margins['bottom'])
    
    def save(self):
        self.canvas.save()
        
    def getpdfdata(self):
        return self.canvas.getpdfdata()
