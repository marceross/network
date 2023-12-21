document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener("click", function (event) {
      var toggler = event.target.closest(".text-area-toggler");
      if (toggler) {
        event.preventDefault();
        var postId = toggler.getAttribute("data-post-id");
        toggleTextArea(postId, toggler);
      }
    });
    
    function toggleTextArea(postId, toggler) {
        var textArea = document.getElementById("text-area-" + postId);
        var updateButton = document.querySelector(".update[data-post-id='" + postId + "']");
        
        if (textArea && updateButton) {
          if (textArea.style.display === "none" || textArea.style.display === "") {
            textArea.style.display = "block";
            toggler.style.display = "none";
            updateButton.style.display = "inline-block";
          } else {
            textArea.style.display = "none";
            toggler.style.display = "inline-block";
            updateButton.style.display = "none";
          }
        }
      }
    
        
      var likeForms = document.querySelectorAll(".like-form");
    
      likeForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
          event.preventDefault();
    
          var formData = new FormData(form);
    
          fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
              "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
          })
            .then((response) => response.json())
            .then((data) => {
              if (Array.isArray(data) && data.length > 0) {
                var post = data[0].fields;
                var postId = data[0].pk;
                var likesCountElement = document.getElementById(
                  "likes-count-" + postId
                );
                var likeButton = document.getElementById("like-button-" + postId);
    
                likeButton.innerText = post.likes.includes(post.user_id)
                  ? "Unlike"
                  : "Like";
    
                likesCountElement.innerText = "❤️ " + post.likes.length;
              } else {
                console.error("Invalid data structure:", data);
              }
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        });
      });
    });
    