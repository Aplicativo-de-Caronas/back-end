from flask import Flask, url_for, redirect, make_response, request

app = Flask(__name__)

#app.add_url_rule(rule="/usuario/login",
#                 view_func=function,
#                 methods=['POST']
#                 )

@app.route("/")
def index():
    return redirect(url_for('home'))


@app.route("/home")
def home():
    return make_response({"response": "Está no home"})


@app.errorhandler(404)
def resource_not_found():
    return make_response({"error": "Pagina nao encontrada"}, 404)


if __name__ == "__main__":
    app.run()