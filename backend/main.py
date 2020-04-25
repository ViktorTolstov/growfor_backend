from app import app

if __name__ == 'main':
    app.run(ssl_context=('cert.pem', 'key.pem'))
