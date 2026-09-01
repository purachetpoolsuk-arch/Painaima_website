import os
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "painaima_core.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from accounts.models import Profile, Follow
from posts.models import Post, Tag, Like, Comment, Bookmark, Story


def generate_sample_image(text, bg_gradient_start, bg_gradient_end, subtext=""):
    """Generates an aesthetic modern sample image with gradient background."""
    width, height = 800, 800
    base = Image.new("RGB", (width, height), bg_gradient_start)
    draw = ImageDraw.Draw(base)

    # Simple vertical gradient interpolation
    for y in range(height):
        r = int(bg_gradient_start[0] + (bg_gradient_end[0] - bg_gradient_start[0]) * (y / height))
        g = int(bg_gradient_start[1] + (bg_gradient_end[1] - bg_gradient_start[1]) * (y / height))
        b = int(bg_gradient_start[2] + (bg_gradient_end[2] - bg_gradient_start[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add stylish circles/decorations
    draw.ellipse([width - 250, -100, width + 250, 400], fill=(255, 255, 255, 30))
    draw.ellipse([-150, height - 350, 350, height + 150], fill=(255, 255, 255, 20))

    # Draw centered frame
    draw.rounded_rectangle([60, 60, width - 60, height - 60], radius=24, outline=(255, 255, 255, 120), width=3)

    # We can draw sample text in the middle
    buffer = BytesIO()
    base.save(buffer, format="JPEG", quality=90)
    return ContentFile(buffer.getvalue())


def run_seed():
    print("Seeding sample data for Painaima...")

    # 1. Create Superuser / Admin
    admin_user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@painaima.local"})
    if created:
        admin_user.set_password("admin123")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        admin_user.profile.full_name = "Painaima Admin"
        admin_user.profile.bio = "ผู้ดูแลระบบ Painaima ✨ ยินดีต้อนรับทุกคนครับ"
        admin_user.profile.location = "Bangkok, Thailand"
        admin_user.profile.save()
        print("Created superuser: admin / admin123")

    # 2. Create Demo Users
    demo_users_data = [
        {
            "username": "nat_traveler",
            "full_name": "ณัฐ สายเที่ยว ✈️",
            "bio": "หลงรักการเดินทางและคาเฟ่ลับๆ ☕📸 | Wanderlust & Photography",
            "location": "เชียงใหม่, ประเทศไทย",
            "website": "https://instagram.com",
        },
        {
            "username": "ploy_cafehopping",
            "full_name": "Ploy Ploy 🍰",
            "bio": "Weekend coffee addict ☕✨ ตามหาคาเฟ่แสงสวยทั่วกรุงเทพฯ",
            "location": "Ari, Bangkok",
            "website": "https://ploycafe.blog",
        },
        {
            "username": "ken_mountain",
            "full_name": "Ken Outdoor 🏕️",
            "bio": "แคมป์ปิ้ง ภูเขา ทะเลหมอก | กางเต็นท์รับลมหนาว",
            "location": "เขาใหญ่, นครราชสีมา",
            "website": "https://kenoutdoor.me",
        },
        {
            "username": "mali_foodie",
            "full_name": "Mali Food & Vibe 🍜",
            "bio": "ของกินอร่อยอยู่ที่ไหน เราจะไปที่นั่น! Street food lover",
            "location": "Yaowarat, Bangkok",
            "website": "",
        },
    ]

    users = {}
    for u_data in demo_users_data:
        user, u_created = User.objects.get_or_create(
            username=u_data["username"],
            defaults={"email": f"{u_data['username']}@painaima.local"}
        )
        if u_created:
            user.set_password("password123")
            user.save()
        
        user.profile.full_name = u_data["full_name"]
        user.profile.bio = u_data["bio"]
        user.profile.location = u_data["location"]
        user.profile.website = u_data["website"]
        user.profile.save()
        users[u_data["username"]] = user

    print(f"Created {len(users)} demo users.")

    # 3. Create Follow connections
    Follow.objects.get_or_create(follower=admin_user, following=users["nat_traveler"])
    Follow.objects.get_or_create(follower=admin_user, following=users["ploy_cafehopping"])
    Follow.objects.get_or_create(follower=users["nat_traveler"], following=users["ploy_cafehopping"])
    Follow.objects.get_or_create(follower=users["nat_traveler"], following=users["ken_mountain"])
    Follow.objects.get_or_create(follower=users["ploy_cafehopping"], following=users["nat_traveler"])
    Follow.objects.get_or_create(follower=users["ken_mountain"], following=admin_user)

    # 4. Create Posts
    posts_data = [
        {
            "author": users["ploy_cafehopping"],
            "caption": "แวะมาจิบกาแฟ Dirty ร้านลับย่านอารีย์ บรรยากาศดี แสงตอนบ่ายคือละมุนมาก ☕🥐 #cafehopping #bkkcafe #vibe #coffeetime @nat_traveler",
            "location": "Ari Soi 4, Bangkok",
            "colors": ((255, 126, 95), (254, 180, 123)),
        },
        {
            "author": users["nat_traveler"],
            "caption": "วิวพระอาทิตย์ตกที่ดอยอินทนนท์ สวยจนลืมหายใจ ทะเลหมอกแน่นๆ อากาศ 12 องศา ฟินมากกก 🌄🍃 #เที่ยวไทย #เชียงใหม่ #sunset #nature @ken_mountain",
            "location": "ดอยอินทนนท์, เชียงใหม่",
            "colors": ((74, 0, 224), (142, 45, 226)),
        },
        {
            "author": users["ken_mountain"],
            "caption": "กางเต็นท์นอนดูดาวที่เขาใหญ่ คืนนี้ดาวเต็มฟ้า อากาศเย็นสบาย ชงกาแฟดริปยามเช้า ⛺🌌 #camping #เขาใหญ่ #outdoor #slowlife",
            "location": "อุทยานแห่งชาติเขาใหญ่, นครราชสีมา",
            "colors": ((17, 153, 142), (56, 239, 125)),
        },
        {
            "author": users["mali_foodie"],
            "caption": "เดินตะลุยกินเยาวราชตอนดึก ก๋วยจั๊บน้ำใสเจ้าดัง ขนมปังปิ้งไส้ทะลัก อร่อยฟินตัวแตก! 🥢🍲 #เยาวราช #streetfood #foodie #bkkfood",
            "location": "ถนนเยาวราช, กรุงเทพฯ",
            "colors": ((241, 39, 17), (245, 175, 25)),
        },
        {
            "author": admin_user,
            "caption": "ยินดีต้อนรับทุกคนเข้าสู่คอมมูนิตี้ Painaima! มาแชร์รูปภาพ ทริปท่องเที่ยว คาเฟ่สวยๆ กันได้เลยครับ 🎉✨ #painaima #welcome #community #travelcommunity",
            "location": "Bangkok, Thailand",
            "colors": ((244, 63, 94), (139, 92, 246)),
        },
    ]

    created_posts = []
    for i, p_info in enumerate(posts_data):
        post = Post.objects.filter(caption=p_info["caption"]).first()
        if not post:
            post = Post(
                author=p_info["author"],
                caption=p_info["caption"],
                location=p_info["location"],
            )
            img_file = generate_sample_image(
                p_info["location"],
                p_info["colors"][0],
                p_info["colors"][1]
            )
            post.image.save(f"sample_post_{i+1}.jpg", img_file, save=True)
            created_posts.append(post)

    print(f"Created {len(created_posts)} demo posts.")

    # 5. Create Sample Stories
    Story.objects.all().delete()
    for u_key in ["ploy_cafehopping", "nat_traveler", "ken_mountain"]:
        u = users[u_key]
        p = u.posts.first()
        if p:
            Story.objects.create(
                user=u,
                media_file=p.image,
                media_type="image",
                caption=f"Today's story by @{u.username} ✨",
                shared_post=p,
            )
    print("Created sample stories.")

    # 6. Create Likes and Comments
    for post in Post.objects.all():
        # Like from admin and other users
        Like.objects.get_or_create(user=admin_user, post=post)
        Like.objects.get_or_create(user=users["nat_traveler"], post=post)
        
        # Add sample comments
        Comment.objects.get_or_create(
            user=users["ploy_cafehopping"],
            post=post,
            defaults={"text": "รูปสวยมากกก แสงดีสุดๆ เลยค่ะ 😍✨"}
        )
        Comment.objects.get_or_create(
            user=users["ken_mountain"],
            post=post,
            defaults={"text": "บรรยากาศดูดีมาก อยากตามไปเช็คอินเลยครับ 👍"}
        )

    print("Sample seeding completed successfully!")


if __name__ == "__main__":
    run_seed()
