import bottle 
import os



app = bottle.Bottle()


@app.route('/ticket/<ticket_id>')
def __serve_ticket(ticket_id):
    pdf_folder = 'tickets'
    
    pdf_path = os.path.join(pdf_folder, f'{ticket_id}.pdf')
    
    if os.path.isfile(pdf_path):
        return bottle.static_file(f'{ticket_id}.pdf', root=pdf_folder, mimetype='application/pdf')
    else:
        return "Ticket not found", 404
    
def run_server():
    app.run(host='localhost', port=8080)
    
