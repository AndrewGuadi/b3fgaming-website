# populate_platforms.py

from app import app, db
from models import Platform

def populate_platforms():
    platforms = [
        {'name': 'Twitch', 'icon_class': 'fab fa-twitch'},
        {'name': 'YouTube', 'icon_class': 'fab fa-youtube'},
        {'name': 'Facebook', 'icon_class': 'fab fa-facebook'},
        {'name': 'Twitter', 'icon_class': 'fab fa-twitter'},
        {'name': 'Instagram', 'icon_class': 'fab fa-instagram'},
        {'name': 'LinkedIn', 'icon_class': 'fab fa-linkedin'},
        {'name': 'Discord', 'icon_class': 'fab fa-discord'},
        {'name': 'Reddit', 'icon_class': 'fab fa-reddit'},
        {'name': 'Snapchat', 'icon_class': 'fab fa-snapchat'},
        {'name': 'Pinterest', 'icon_class': 'fab fa-pinterest'},
        {'name': 'TikTok', 'icon_class': 'fab fa-tiktok'},
        {'name': 'GitHub', 'icon_class': 'fab fa-github'},
        {'name': 'Slack', 'icon_class': 'fab fa-slack'},
        {'name': 'Medium', 'icon_class': 'fab fa-medium'},
        {'name': 'Spotify', 'icon_class': 'fab fa-spotify'},
        {'name': 'SoundCloud', 'icon_class': 'fab fa-soundcloud'},
        {'name': 'Tumblr', 'icon_class': 'fab fa-tumblr'},
        {'name': 'Vimeo', 'icon_class': 'fab fa-vimeo'},
        {'name': 'Telegram', 'icon_class': 'fab fa-telegram'},
        {'name': 'WhatsApp', 'icon_class': 'fab fa-whatsapp'},
        {'name': 'Weibo', 'icon_class': 'fab fa-weibo'},
        {'name': 'Quora', 'icon_class': 'fab fa-quora'},
        {'name': 'Flickr', 'icon_class': 'fab fa-flickr'},
        {'name': 'Dribbble', 'icon_class': 'fab fa-dribbble'},
        {'name': 'Behance', 'icon_class': 'fab fa-behance'},
        {'name': 'VK', 'icon_class': 'fab fa-vk'},
        {'name': 'Mixcloud', 'icon_class': 'fab fa-mixcloud'},
        {'name': 'Deezer', 'icon_class': 'fab fa-deezer'},
        {'name': 'Dailymotion', 'icon_class': 'fab fa-dailymotion'},
        {'name': 'Rumble', 'icon_class': 'fab fa-rumble'},
        {'name': 'Clubhouse', 'icon_class': 'fas fa-microphone-alt'}  # Assuming no brand icon
        # Add more platforms as needed
    ]

    with app.app_context():
        for platform in platforms:
            existing = Platform.query.filter_by(name=platform['name']).first()
            if not existing:
                new_platform = Platform(name=platform['name'], icon_class=platform['icon_class'])
                db.session.add(new_platform)
        db.session.commit()
        print("Platform table populated successfully.")

if __name__ == '__main__':
    populate_platforms()
