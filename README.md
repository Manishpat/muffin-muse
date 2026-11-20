# Muffin Muse – By Diksha

Website for **Muffin Muse**, handcrafted celebration cakes by Diksha. It's a static site (HTML, CSS and plain JavaScript) with no build step, hosted free on GitHub Pages.

## Structure

```
index.html            Home page: hero, story, collection, gallery, how-to-order, why us, testimonials, booking, Instagram, footer
thanks.html           Page FormSubmit redirects to after a booking with a photo is accepted
assets/css/styles.css Design system and layout
assets/js/config.js   ← The only file you normally edit (Instagram, WhatsApp, booking email, lead time)
assets/js/app.js      Navigation, collection cards, gallery and lightbox, testimonials, Instagram grid
assets/js/booking.js  Booking form: steps, conditional questions, validation, summary, email sending
assets/img/           Optimised WebP photos (large + `-sm` mobile versions)
```

## Booking emails (FormSubmit.co)

Each booking is emailed to the address in `assets/js/config.js` (`formEndpointId`) through [FormSubmit](https://formsubmit.co). It's free and needs no backend or login.

* **Without a photo:** the form posts to FormSubmit's AJAX endpoint. Success is shown only when FormSubmit replies `success: true`.
* **With a reference photo:** the form sends a multipart post with the photo attached. FormSubmit redirects to `thanks.html` only after it accepts the booking, and that page tells the booking form it worked. Anything else counts as a failure, and the customer can retry, send without the photo, copy their details or DM on Instagram.

### One-time setup

1. Submit one test booking from the live site.
2. FormSubmit emails **"Action Required: Activate FormSubmit"** to the booking inbox. Click **Activate Form**. Bookings sent before activation are not delivered, and the site says so.
3. Optional but recommended: the activation email includes a random alias string. Paste it into `formEndpointId` in `config.js` in place of the plain email address, so the address isn't visible in the page source.

## Common edits

* **WhatsApp button:** set `whatsappNumber` in `config.js`, for example `"919876543210"`. When it's empty, every WhatsApp button stays hidden.
* **Testimonials:** the `QUOTES` list in `assets/js/app.js` holds sample quotes. Replace them with real customer reviews.
* **Photos:** the images are high-quality stock photos (Unsplash licence). Replace the files in `assets/img/` with Diksha's own cake photos, keeping the same file names, ideally WebP and about 1000px wide plus a 560px `-sm` version.
* **Notice period:** `minLeadDays` in `config.js`.

## Deploy

Any push to `main` is published by GitHub Pages (Settings → Pages → Deploy from branch → `main` / root).
