Obiadekchan is an imageboard engine that I've developed using Django Python framework for the back-end. For the front-end, nothing fancy, just plain old HTML, CSS and JavaScript with bits of jQuery here and there (btw I am beginning to work on my next project right now, which is going to be single page application written in vue.js and few other libraries).

There is a 5 page limit with 10 posts each page, after it's reached, if somoene where to post a new thread, the last one is going down. Pretty common on imageboards I'd say.

Here's how it looks:
![screenshot](http://i.imgur.com/kr35YSe.jpg)

There's a password (generated automatically on the front-end and stored in localStorage) which is used for deleting posts and signing them as a creator of a given thread. It is also possible to sign a post as a moderator (of course you have to be a moderator to do that).
Users also have the ability to report posts (even multiple ones at once), and there is basic moderator panel, in which you can also sort posts by user IP.
![screenshot](http://i.imgur.com/LRPrmr5.png)
![sc](https://i.imgur.com/1iFB3PH.png)

I've implemented post preview using jquery's ajax. When script detects '>>xx' tag in someone's post it add's to it <a href> element which on click takes user to thread in which the post is and on hover it generates another link (second link is based on data-id attritbute of the first one), loads the post with ajax and injects it into invisible span element next to every '>xx' link. It also adds an adnotation under a cited post.
This is how it looks.
![sc](https://i.imgur.com/04AmhrT.jpg)

There are also some theme settings, user can change background color, font of posts, font of every other element, as well as font size.
![sc](https://i.imgur.com/jIOkh6U.png)
