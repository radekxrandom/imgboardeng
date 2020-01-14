Obiadekchan is an imageboard engine that I've developed using Django Python framework for the back-end. For the front-end, nothing fancy, just plain old HTML, CSS and JavaScript with bits of jQuery here and there (btw I am beginning to work on my next project right now, which is going to be single page application written in vue.js and few other libraries).

There is a 5 page limit with 10 posts each page, after it's reached, if somoene where to post a new thread, the last one is going down. Pretty common on imageboards I'd say.

Here's how it looks:
![screenshot](https://i.imgur.com/aWGjy7D.png)

There is a quick reply feature. When you click given post id while holding ctrl pop up form appears on the right. In this form you can post answer (using AJAX) from the main board to any thread without going inside of it first. Pop up form is draggable and can be closed.
![sc](https://i.imgur.com/eZQcIJe.png)

While inside a given thread, on the bottom of it, you can check a checkbox in order to turn the auto refresh feature on. While turned on, it checks for a new posts in a given thread every x seconds. Waiting time increases for every unsuccessful check (increments differ), and stalls at a 60 seconds. Should there be any new posts, waiting time is reset to original value. Checking and loading new posts is done with AJAX without having to reload the page. Checkbox value is remembered and set automatically the next time.
https://i.imgur.com/rCPEYUZ.gifv

There's a password (generated automatically on the front-end and stored in localStorage) that is used for deleting posts and signing them as the creator of a given thread. It is also possible to sign posts as a moderator (of course you have to be a moderator in order to do that).
Users also have the ability to report posts (even multiple ones at once), and there is a basic moderator panel, in which you can also sort posts by user IP.
![screenshot](https://i.imgur.com/e8vEJEn.png)
![sc](https://i.imgur.com/1iFB3PH.png)

I've implemented post preview using jquery's ajax. When script detects '>>xx' tag in someone's post it add's to it a href element which on click takes user to thread in which the post is and on hover it generates another link (second link is based on data-id attritbute of the first one), loads the post with ajax and injects it into invisible span element next to every '>xx' link. It also adds an adnotation under a cited post.
This is how it looks.
![sc](https://i.imgur.com/04AmhrT.jpg)

I've also included some post styling abilities (something like bbcode), users can use spoilers, bold text, and should user post a link it's automatically processed to be an a href element.
![sc](https://i.imgur.com/sb7XCgM.png)

There are also some theme settings, user can change background color, font of posts, font of every other element, as well as font size.
![sc](https://i.imgur.com/jIOkh6U.png)


As many people choose to surf the web from mobile devices, I have taken much care in making my imageboard responsive, and as far as imageboards go it looks rather decent on small screens. 
<center><p style='  text-align:center'>
<img src='https://i.imgur.com/2tiUSTx.png' width='200' height='410'/><img src='https://i.imgur.com/3uGgpvH.png' width='200' height='410'/>
  </p></center>
