# Make Fragrance Browsing Fast & Sleek

The catalogue currently has two performance bottlenecks: **images load slowly** (every image goes through a Django proxy that fetches from the source URL, strips the background, and converts to WebP — cold cache hits are 2-5s each), and **loading more fragrances requires a button click + full re-render wait**. This plan attacks both sides — frontend image loading UX and backend image throughput — to make browsing feel instant.

## Root Causes Identified

1. **Image proxy is slow on cold cache** — [`fragrance_image`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/catalog/views.py#L482-L499) fetches the source URL, runs PIL background removal, and converts to WebP *synchronously* on every cold request. Even with the file-based cache, first loads for each fragrance are 2-5 seconds.
2. **No image preloading on the frontend** — The `<img>` tags use `loading="lazy"` but there's no progressive placeholder/blur or preloading of the next page's images.
3. **"Load More" is manual** — Users must click a button and wait for both the API response *and* all new images to load. There's no infinite scroll or prefetching.
4. **No thumbnail/small variant** — List views load the same 300px WebP as the detail page. A smaller variant would be much faster for grids.
5. **`warm_images.py` has stale cache key** — It checks `fragrance_image_v2_{pk}` but the view uses `fragrance_image_v3_{pk}`, so the warmup command is a no-op.

## Proposed Changes

### Backend: Smaller Thumbnails + Fix Warm Script

#### [MODIFY] [`views.py`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/catalog/views.py)

- Add a `size` query parameter to `fragrance_image()`: `?size=thumb` returns a 120px thumbnail, default stays at 300px
- Use separate cache keys for thumb vs full: `fragrance_image_v3_{pk}_thumb` / `fragrance_image_v3_{pk}_full`
- Both sizes get generated and cached on first request to the full-size image (generate thumb at the same time since we already have the PIL image open)

#### [MODIFY] [`serializers.py`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/catalog/serializers.py)

- Add a `thumbnail_url` field to `FragranceListSerializer` that appends `?size=thumb` to the image URL — list views use the small version, detail page uses the full version

#### [MODIFY] [`warm_images.py`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/catalog/management/commands/warm_images.py)

- Fix the stale cache key check from `v2` → `v3`
- Warm both `thumb` and `full` variants

---

### Frontend: Progressive Image Loading + Infinite Scroll + Prefetch

#### [NEW] [`OptimizedImage.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/components/common/OptimizedImage.tsx)

A reusable image component with:
- **Shimmer placeholder** while loading (uses the existing `bg-surface animate-pulse` style)
- **Fade-in transition** when the image loads (`opacity-0` → `opacity-100`)
- **IntersectionObserver**-based lazy loading with generous rootMargin (start loading images 400px *before* they scroll into view)
- **`decoding="async"`** + **`fetchpriority="low"`** for grid images to avoid blocking the main thread

#### [MODIFY] [`FragranceCard.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/components/catalog/FragranceCard.tsx)

- Replace the raw `<img>` with `<OptimizedImage>` using the `thumbnail_url` for the grid
- The `thumbnail_url` loads the smaller 120px image, cutting transfer size ~75%

#### [MODIFY] [`HomePage.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/pages/HomePage.tsx)

- Replace "Load More" button with **infinite scroll** using IntersectionObserver on a sentinel element
- **Prefetch next page** — when the current page loads, immediately fire a react-query prefetch for `page + 1` so the data is already cached by the time the user scrolls down
- Keep the "Load More" button as a fallback (shown if JS IntersectionObserver isn't supported or user prefers reduced motion)

#### [MODIFY] [`HouseDetailPage.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/pages/HouseDetailPage.tsx)

- Replace inline `<img>` with `<OptimizedImage>` for consistency

#### [MODIFY] [`FragranceDetailPage.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/pages/FragranceDetailPage.tsx)

- Use `<OptimizedImage>` for the hero bottle image (full-size URL, not thumbnail)

#### [MODIFY] [`SearchModal.tsx`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/components/common/SearchModal.tsx)

- Use `<OptimizedImage>` for search result thumbnails

---

### Frontend Types Update

#### [MODIFY] [`types/index.ts`](file:///c:/Users/Riddo/Desktop/Drydwn/drydwn/frontend/src/types/index.ts)

- Add `thumbnail_url: string | null` to `FragranceItem` and `FragranceMinimal`

## Verification Plan

### Manual Verification
- Scroll through the catalogue on the home page — images should show a shimmer placeholder and fade in smoothly
- Scrolling down should automatically load the next page before the user reaches the bottom
- Opening the network tab should confirm thumbnail images are ~120px and much smaller than the full 300px versions
- Fragrance detail page should still load the full-size image
- The warm_images management command should correctly check and warm both thumb/full variants
