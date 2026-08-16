from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils import analyze_face
import os

def faceshape(request):
    """
    Unified view for both Live and Upload modes.
    """
    context = {
        "mode": request.GET.get("mode", "live"),  # default to live
    }

    # Handle image upload
    if request.method == "POST" and request.FILES.get("photo"):
        photo = request.FILES["photo"]
        fs = FileSystemStorage()
        filename = fs.save(photo.name, photo)
        filepath = fs.path(filename)

        gender = request.POST.get("gender", "unisex")
        
        result = analyze_face(
            filepath,
            gender=gender,
            use_llm=True,
            extra={
                "hair_length": request.POST.get("hair_length", "any"),
                "hair_texture": request.POST.get("hair_texture", "any"),
                "lifestyle": request.POST.get("lifestyle", "everyday"),
            }
        )

        context.update({
            "mode": "upload",
            "result": result,
            "uploaded_url": fs.url(filename),
            "gender": gender,
        })

        # Optional: delete file after analysis to save space
        try:
            os.remove(filepath)
        except:
            pass

    return render(request, "face_live.html", context)