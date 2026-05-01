from datetime import datetime
from io import BytesIO
import os

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from models import CollectionTypes, Film
from services import JeuVideoService

app = Flask(__name__)
CORS(app)


COLLECTION_ITEMS = {
    CollectionTypes.Films.value: [
        Film(id=1, name="Interstellar"),
        Film(id=2, name="Inception"),
        Film(id=3, name="Le Seigneur des Anneaux"),
    ],
}

@app.get("/api/time")
def get_time():
    return jsonify(
        {
            "message": "Hello World depuis Python!",
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


@app.get("/collections/<collection_type>/search")
def search_collection_items(collection_type):
    try:
        collection_enum = CollectionTypes(collection_type)
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Unknown collection type.",
                    "allowed_types": [t.value for t in CollectionTypes],
                }
            ),
            400,
        )

    search_query = request.args.get("q", "").strip().lower()
    if collection_enum == CollectionTypes.JeuxVideo:
        platform = request.args.get("platform", "Playstation").strip() or "Playstation"
        try:
            items = JeuVideoService().search(platform=platform, query=search_query)
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Sheet '{platform}' not found in ODS file.",
                        "hint": "Use query param ?platform=<sheet_name>.",
                    }
                ),
                400,
            )
        except Exception as exc:
            return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500
    else:
        items = COLLECTION_ITEMS[collection_enum.value]

    if search_query and collection_enum != CollectionTypes.JeuxVideo:
        items = [
            item
            for item in items
            if search_query
            in " ".join(str(value).lower() for value in item.to_dict().values())
        ]

    if collection_enum == CollectionTypes.JeuxVideo:
        return jsonify(items)

    return jsonify({"type": collection_enum.value, "items": [item.to_dict() for item in items]})


@app.get("/collections/JeuxVideo/platforms")
def list_jeux_video_platforms():
    try:
        platforms = JeuVideoService().list_platforms()
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "platforms": platforms})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500


@app.get("/collections/JeuxVideo/home")
def get_jeux_video_home():
    try:
        stats = JeuVideoService().get_home_stats()
        return jsonify({"type": CollectionTypes.JeuxVideo.value, **stats})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Sheet 'Accueil' not found in ODS file.",
                }
            ),
            400,
        )
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500


@app.get("/collections/JeuxVideo/game-search")
def search_jeux_video_games():
    search_query = request.args.get("q", "").strip()
    limit = request.args.get("limit", "50").strip()
    try:
        parsed_limit = max(1, min(int(limit), 100))
    except ValueError:
        parsed_limit = 50

    try:
        items = JeuVideoService().search_by_game_name(
            query=search_query,
            limit=parsed_limit,
        )
        return jsonify(
            {
                "type": CollectionTypes.JeuxVideo.value,
                "query": search_query,
                "count": len(items),
                "items": items,
            }
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Unable to search ODS file: {exc}"}), 500


@app.post("/collections/JeuxVideo/games")
def add_jeux_video_game():
    payload = request.get_json(silent=True) or {}
    try:
        item = JeuVideoService().add_game(payload)
        return jsonify({"type": CollectionTypes.JeuxVideo.value, "item": item}), 201
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unable to update ODS file: {exc}"}), 500


@app.get("/collections/JeuxVideo/platform-image/<path:platform>")
def get_jeux_video_platform_image(platform):
    try:
        image_bytes, mime_type, filename = JeuVideoService().get_platform_image(platform)
        return send_file(
            BytesIO(image_bytes),
            mimetype=mime_type,
            download_name=filename,
            max_age=3600,
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS image: {exc}"}), 500


@app.get("/collections/JeuxVideo/column-values")
def list_jeux_video_column_values():
    platform = request.args.get("platform", "Playstation").strip() or "Playstation"
    try:
        values = JeuVideoService().list_column_values(platform=platform)
        return jsonify(
            {
                "type": CollectionTypes.JeuxVideo.value,
                "platform": platform,
                "values_by_column": values,
            }
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError:
        return (
            jsonify(
                {
                    "error": f"Sheet '{platform}' not found in ODS file.",
                    "hint": "Use query param ?platform=<sheet_name>.",
                }
            ),
            400,
        )
    except Exception as exc:
        return jsonify({"error": f"Unable to read ODS file: {exc}"}), 500


if __name__ == "__main__":
    backend_port = int(os.getenv("BACKEND_PORT", "7777"))
    app.run(debug=True, host="0.0.0.0", port=backend_port)
