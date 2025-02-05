from flask import Flask
from flask_graphql import GraphQLView
from app.graphql.schema import schema
from app.database.schema import init_db

def create_app():
    app = Flask(__name__)
    
    # Add GraphQL view
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )
    
    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    
    return app 