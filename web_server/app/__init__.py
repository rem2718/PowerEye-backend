# web_server\app\__init__.py
from flask import Flask, jsonify,request 
from .extensions import db,bcrypt,csrf
from .models.user_model import User  #Import the relevant model
from .models.room_model import Room  #Import the relevant model
# from .models.user_model import User  #Import the relevant model
# from .models.user_model import User  #Import the relevant model
# from .models.user_model import User  #Import the relevant model
import asyncio



def create_app(config_object='app.config'):
    app = Flask(__name__)

    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # @app.route('/test_mongodb_user')
    # def test_mongodb_user():
    #     document = User.objects.first()
    #     if document is not None:
    #         return jsonify(document.to_json())
    #     else:
    #         return jsonify({'message': 'No document found'})
    
    
    @app.route('/delete_all_rooms', methods=['GET'])
    def delete_all_rooms():
        if request.method == 'GET':
            try:
                # Delete all documents in the collection
                result = Room.objects.delete()
                return jsonify({'message': f'Deleted {result} room documents'})
            except Exception as e:
                return jsonify({'error': str(e)})
    
    @app.route('/test_mongodb_room')
    def test_mongodb_room():
        user = User.objects.get(id="64d154bc94895e0b4c1bc080")  

        # Create a new room
        room = Room(
            name="Living Room",
            user_id=user
        )

        room.save()

        # Assuming you want to add the first three appliances from the user's list
        for appliance in user.appliances[:3]:
            room.appliances.append(appliance)

        room.save()

        document = Room.objects.first()
        if document is not None:
            return jsonify(document.to_json())
        else:
            return jsonify({'message': 'No document found'})


    
    # Register blueprints
    from .controllers import user_controller, energy_controller, appliance_controller, room_controller

    return app