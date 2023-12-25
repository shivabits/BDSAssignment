from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import pandas as pd


app = Flask(__name__)

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb+srv://2022og04034:uwDVTXTWPQyMWn3u@cluster0.jihufmw.mongodb.net/SpotifyMusic'
mongo = PyMongo(app)

class MusicRecommendationSystem:
    def __init__(self):
        self.tracks_collection = mongo.db.SpotifyMusic


    def get_recommendations(self, user_preference):
        # Assume user_id is provided by the user
        preferred_track = self.tracks_collection.find_one({'track_name': user_preference})

        if preferred_track is None:
            return {'message': 'No tracks found.'}

        # Fetch the features of the user's preferred track
        preferred_track_features = {
            'danceability': preferred_track.get('danceability', 0.5),
            'energy': preferred_track.get('energy', 0.5),
            'valence': preferred_track.get('valence', 0.5)
        }

        # For simplicity, we'll recommend tracks with similar features
        similar_tracks = self.tracks_collection.find({
            'danceability': {'$gte': preferred_track_features['danceability'] - 0.1,
                             '$lte': preferred_track_features['danceability'] + 0.1},
            'energy': {'$gte': preferred_track_features['energy'] - 0.1,
                       '$lte': preferred_track_features['energy'] + 0.1},
            'valence': {'$gte': preferred_track_features['valence'] - 0.1,
                        '$lte': preferred_track_features['valence'] + 0.1}
        }).limit(5)

        recommendations = [str(track['_id']) for track in similar_tracks]

        # Convert recommendations to a DataFrame
        recommendations_df = pd.DataFrame({'track_name': [user_preference] * len(recommendations),
                                           'recommended_track_id': recommendations})

        return recommendations_df.to_dict(orient='records')

# Create an instance of MusicRecommendationSystem
music_recommendation_system = MusicRecommendationSystem()

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()

    if 'user_preference' not in data:
        return jsonify({'error': 'Missing user_preference parameter'}), 400

    user_preference = data['user_preference']
    recommendations = music_recommendation_system.get_recommendations(user_preference)

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
