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

* Every booking posts to FormSubmit's AJAX endpoint. Success is shown only when FormSubmit replies `success: true`. Otherwise the customer sees "not sent", with options to retry, copy their details or DM on Instagram.
* **Reference photos:** in testing (Nov 2026), FormSubmit's free service answered "Access Denied" to file uploads, so `photoAttachments` is `false`. The booking still arrives, and the email notes that the customer has a photo. After booking, the customer gets a one-tap **Share photo with Diksha** button (the phone share sheet, for Instagram or WhatsApp) plus Instagram/WhatsApp links, all quoting the booking reference.
* `photoAttachments: true` switches to an attachment upload in a hidden iframe. FormSubmit redirects to `thanks.html` only after it accepts the email, so a refused upload is never shown as a success. Turn it on only after you've confirmed FormSubmit accepts attachments for your form, for example after switching to the alias.

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
