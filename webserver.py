from flask import Flask, Response, jsonify
from flask_cors import CORS
import video_parser

app = Flask(__name__)
CORS(app)
key = 'YOUR_API_KEY'
jsonifier = video_parser.YoutubeVideoJson(key)


@app.route("/api/videos/full/<string:channel_id>")
def videos_full(channel_id):
    try:
        info = jsonifier.get_channel_videos_full_info(channel_id)
    except video_parser.ChannelNotFoundException as e:
        return jsonify({'error': e.message, 'error_code': e.code})
    except TypeError as e:
        return jsonify({'error': str(e)})
    return Response(response=info,
                    status=200,
                    mimetype="application/json")


@app.route("/api/videos/short/<string:channel_id>")
def videos_short(channel_id):
    try:
        info = jsonifier.get_channel_videos_short_info(channel_id)
    except video_parser.ChannelNotFoundException as e:
        return jsonify({'error': e.message, 'error_code': e.code})
    except TypeError as e:
        return jsonify({'error': str(e)})
    return Response(response=info,
                    status=200,
                    mimetype="application/json")


@app.route("/api/videos/ids/<string:channel_id>")
def videos_ids(channel_id):
    try:
        info = jsonifier.get_channel_videos_ids(channel_id)
    except video_parser.ChannelNotFoundException as e:
        return jsonify({'error': e.message, 'error_code': e.code})
    except TypeError as e:
        return jsonify({'error': str(e)})
    return Response(response=info,
                    status=200,
                    mimetype="application/json")


if __name__ == "__main__":
    app.run()
