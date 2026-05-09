import qrcode
import base64
import datetime
import pdf_server
import os

def gen_qr_via_endpoint(ticket_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"http://localhost:8080/ticket/{ticket_id}")
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    img.save(f"./qrs/{ticket_id}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png", format="PNG")
    return f"./qrs/{ticket_id}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    