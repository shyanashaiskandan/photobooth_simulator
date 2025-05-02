from django.shortcuts import render, redirect
from django.conf import settings
import os
from .photobooth import capture_photos, return_prompt, send_email_with_photos, upload_to_s3

def photobooth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            photo_files = capture_photos()  # Returns a list of filenames
            request.session['photo_files'] = photo_files
            ai_prompt = return_prompt(photo_files)
            request.session['ai_prompt'] = ai_prompt
            return redirect('photobooth')
        elif action == 'done':
            photo_files = request.session.get('photo_files', [])
            s3_urls = []
            # Upload each photo to S3 and collect the URLs
            for file in photo_files:
                full_path = os.path.join(settings.MEDIA_ROOT, file)
                url = upload_to_s3(full_path)
                if url:
                    s3_urls.append(url)
            # If an email address is provided, send an email with the S3 URLs.
            email_address = request.POST.get('email')
            if email_address:
                email_pass_file = "/home/shyana/.local/share/.email_password"
                if os.path.exists(email_pass_file):
                    with open(email_pass_file, "r") as f:
                        password = f.read().strip()
                    import yagmail
                    yag = yagmail.SMTP("photobooth263@gmail.com", password)
                    # This function would send the email containing the S3 URLs.
                    send_email_with_photos(yag, email_address, s3_urls)
            # Clear session data and show a completion page.
            request.session['photo_files'] = []
            request.session['ai_prompt'] = ""
            return render(request, 'booth/complete.html', {'s3_urls': s3_urls})
    else:
        photo_files = request.session.get('photo_files', [])
        ai_prompt = request.session.get('ai_prompt', '')
        context = {
            'photo_files': photo_files,
            'ai_prompt': ai_prompt,
            'media_url': settings.MEDIA_URL,
        }
        return render(request, 'booth/index.html', context)