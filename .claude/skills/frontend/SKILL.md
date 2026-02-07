---
name: nextjs-frontend
description: Build production-grade Next.js 16 applications with modern architecture. Use this skill when building Next.js pages, components, layouts, or full applications. Covers App Router, Server/Client Components, routing, layouts, styling, and performance optimization. Focuses on Next.js 16 best practices and patterns.
license: Complete terms in LICENSE.txt
---

This skill guides the creation of production-grade Next.js 16 applications using the App Router, modern React patterns, and best practices for performance, SEO, and developer experience.

## Next.js 16 Architecture Overview

Next.js 16 uses the App Router (`app/` directory) as the default routing system. Key concepts:

- **Server Components**: Default rendering mode for components (no `"use client"`)
- **Client Components**: Interactive components marked with `"use client"` directive
- **File-based Routing**: Folders define routes, special files define UI
- **Layouts**: Shared UI that persists across routes
- **Route Handlers**: API endpoints defined with `route.ts/js`

## Project Structure

```
app/
├── layout.tsx           # Root layout (required)
├── page.tsx            # Home page (/)
├── globals.css         # Global styles
├── not-found.tsx       # 404 page
├── error.tsx           # Error boundary
├── loading.tsx         # Loading UI
├── (marketing)/        # Route group (doesn't affect URL)
│   ├── layout.tsx      # Marketing layout
│   ├── about/
│   │   └── page.tsx    # /about route
│   └── contact/
│       └── page.tsx    # /contact route
├── dashboard/
│   ├── layout.tsx      # Dashboard layout
│   ├── page.tsx        # /dashboard route
│   └── [id]/           # Dynamic route
│       └── page.tsx    # /dashboard/[id] route
└── api/
    └── users/
        └── route.ts    # API route /api/users

components/              # Reusable components
├── ui/                 # Base UI components
├── features/           # Feature-specific components
└── layouts/            # Layout components

lib/                    # Utilities, helpers, types
public/                 # Static assets
styles/                 # Additional stylesheets
```

## Pages & Routing

### Page Files

Every `page.tsx` file exports a React component that renders the route:

```tsx
// app/page.tsx - Server Component (default)
export default function HomePage() {
  return (
    <main>
      <h1>Welcome to Next.js 16</h1>
    </main>
  );
}
```

### Dynamic Routes

Use brackets for dynamic segments:

```tsx
// app/blog/[slug]/page.tsx
interface PageProps {
  params: { slug: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default function BlogPost({ params, searchParams }: PageProps) {
  return <article>Post: {params.slug}</article>;
}

// Generate static params at build time
export async function generateStaticParams() {
  const posts = await fetchPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```

### Catch-all Routes

```tsx
// app/shop/[...slug]/page.tsx - Matches /shop/a, /shop/a/b, etc.
// app/docs/[[...slug]]/page.tsx - Also matches /docs
```

### Parallel Routes

Use named slots for complex layouts:

```tsx
// app/layout.tsx
export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <>
      {children}
      {team}
      {analytics}
    </>
  );
}

// app/@team/page.tsx
// app/@analytics/page.tsx
```

### Intercepting Routes

Intercept routes for modals/overlays:

```tsx
// app/photos/[id]/page.tsx - Direct navigation
// app/@modal/(.)photos/[id]/page.tsx - Intercepts when navigating from same level
```

## Layouts

### Root Layout (Required)

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'My App',
  description: 'Production-grade Next.js application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Layouts don't re-render on navigation */}
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

### Nested Layouts

Layouts nest and compose:

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <Sidebar />
      <div className="content">{children}</div>
    </div>
  );
}
```

### Route Groups

Group routes without affecting URL structure:

```tsx
// app/(marketing)/layout.tsx - Applies to routes inside (marketing)
// app/(app)/layout.tsx - Different layout for (app) group
// URL remains /about, not /(marketing)/about
```

## Components

### Server Components (Default)

Server Components render on the server and send HTML to the client:

```tsx
// app/components/UserList.tsx (no "use client")
import { db } from '@/lib/db';

export default async function UserList() {
  // Can directly access backend resources
  const users = await db.user.findMany();
  
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

**Benefits:**
- Direct database/API access
- Zero JavaScript sent to client
- Automatic code splitting
- Better SEO

**Limitations:**
- No hooks (useState, useEffect, etc.)
- No event handlers
- No browser APIs

### Client Components

Mark components with `"use client"` for interactivity:

```tsx
// components/Counter.tsx
"use client";

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

**Use Client Components for:**
- Event handlers (onClick, onChange, etc.)
- React hooks (useState, useEffect, useContext, etc.)
- Browser APIs (localStorage, window, etc.)
- Third-party libraries requiring browser environment

### Composition Patterns

**Pass Server Components to Client Components:**

```tsx
// ✅ CORRECT: Pass Server Component as children
"use client";

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  return <div className="wrapper">{children}</div>;
}

// Usage
<ClientWrapper>
  <ServerComponent /> {/* Server Component passed as children */}
</ClientWrapper>

// ❌ INCORRECT: Import Server Component in Client Component
"use client";
import ServerComponent from './ServerComponent'; // Won't work!
```

**Shared Components:**

Place reusable UI in `/components`:

```tsx
// components/ui/Button.tsx
"use client";

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Component Organization

```
components/
├── ui/                    # Base components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   └── Modal.tsx
├── features/              # Feature-specific
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   └── products/
│       ├── ProductCard.tsx
│       └── ProductGrid.tsx
└── layouts/               # Layout components
    ├── Header.tsx
    ├── Footer.tsx
    └── Sidebar.tsx
```

## Styling

### CSS Modules (Built-in)

Scoped CSS with zero runtime:

```tsx
// components/Card.module.css
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

// components/Card.tsx
import styles from './Card.module.css';

export function Card({ title, children }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>{title}</h2>
      {children}
    </div>
  );
}
```

### Tailwind CSS (Recommended)

Install and configure:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```js
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
};
```

```tsx
// Usage
export function Hero() {
  return (
    <section className="bg-gradient-to-r from-brand-500 to-brand-900 text-white py-20">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl md:text-6xl font-bold mb-4">
          Welcome to Next.js 16
        </h1>
      </div>
    </section>
  );
}
```

### Global Styles

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground: #171717;
  --background: #ffffff;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground: #ededed;
    --background: #0a0a0a;
  }
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: var(--font-geist-sans);
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }
  
  .btn-primary {
    @apply bg-brand-500 text-white hover:bg-brand-600;
  }
}
```

### CSS-in-JS

For styled-components or emotion, you need client-side rendering:

```tsx
// components/StyledButton.tsx
"use client";

import styled from 'styled-components';

const StyledButton = styled.button`
  background: linear-gradient(to right, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

export default StyledButton;
```

### Styling Best Practices

1. **Prefer Tailwind for rapid development** - Utility-first, minimal CSS
2. **Use CSS Modules for component-specific styles** - Better for complex components
3. **Global styles in app/globals.css** - Reset, typography, CSS variables
4. **CSS Variables for theming** - Easy dark mode and customization
5. **Avoid inline styles** - Harder to maintain, no pseudo-classes
6. **Mobile-first responsive design** - Use Tailwind breakpoints (sm:, md:, lg:)

## Data Fetching

### Server Components (Async/Await)

```tsx
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 } // Revalidate every hour
  });
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();
  
  return (
    <div>
      {posts.map(post => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  );
}
```

### Caching Strategies

```tsx
// No caching (always fresh)
fetch('https://api.example.com/data', { cache: 'no-store' });

// Static caching (at build time)
fetch('https://api.example.com/data', { cache: 'force-cache' });

// Revalidate after time
fetch('https://api.example.com/data', { 
  next: { revalidate: 60 } // 60 seconds
});

// Revalidate with tags
fetch('https://api.example.com/data', { 
  next: { tags: ['posts'] }
});

// Then revalidate in Server Action:
import { revalidateTag } from 'next/cache';
revalidateTag('posts');
```

### Client-Side Fetching

Use React hooks or SWR/React Query:

```tsx
"use client";

import { useEffect, useState } from 'react';

export function ClientData() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData);
  }, []);
  
  if (!data) return <div>Loading...</div>;
  return <div>{JSON.stringify(data)}</div>;
}
```

## Performance Optimization

### Image Optimization

```tsx
import Image from 'next/image';

export function ProductImage() {
  return (
    <Image
      src="/product.jpg"
      alt="Product"
      width={800}
      height={600}
      priority // Load immediately for above-fold images
      placeholder="blur" // Show blur while loading
      blurDataURL="data:image/..." // Base64 blur
    />
  );
}
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter, Roboto_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

### Loading States

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/3"></div>
    </div>
  );
}
```

### Streaming with Suspense

```tsx
import { Suspense } from 'react';

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<Loading />}>
        <SlowComponent />
      </Suspense>
      <FastComponent />
    </div>
  );
}
```

## Metadata & SEO

### Static Metadata

```tsx
// app/about/page.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn more about our company',
  openGraph: {
    title: 'About Us',
    description: 'Learn more about our company',
    images: ['/og-image.png'],
  },
};

export default function AboutPage() {
  return <div>About</div>;
}
```

### Dynamic Metadata

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}
```

## Best Practices

### 1. Component Design
- **Default to Server Components** - Use `"use client"` only when needed
- **Composition over Props** - Pass components as children
- **Single Responsibility** - Each component does one thing well
- **TypeScript Interfaces** - Define clear prop types

### 2. File Organization
- **Colocation** - Keep related files together
- **Naming Conventions** - PascalCase for components, kebab-case for routes
- **Barrel Exports** - Use index.ts for clean imports

### 3. Styling
- **Consistent Methodology** - Pick Tailwind OR CSS Modules, not both randomly
- **Design System** - Establish colors, spacing, typography early
- **Responsive First** - Mobile-first approach with breakpoints
- **Accessibility** - Semantic HTML, ARIA labels, keyboard navigation

### 4. Performance
- **Image Optimization** - Always use next/image
- **Code Splitting** - Automatic with App Router, use dynamic imports for large components
- **Caching Strategy** - Understand static vs dynamic rendering
- **Lazy Loading** - Load non-critical components on-demand

### 5. State Management
- **URL State** - Use searchParams for shareable state
- **Server State** - Fetch in Server Components when possible
- **Client State** - useState for local, Context for shared
- **Form State** - Use Server Actions for mutations

## Common Patterns

### Protected Routes

```tsx
// app/dashboard/layout.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function DashboardLayout({ children }) {
  const session = await getSession();
  
  if (!session) {
    redirect('/login');
  }
  
  return <div>{children}</div>;
}
```

### Error Boundaries

```tsx
// app/error.tsx
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### API Routes

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const posts = await db.post.findMany();
  return NextResponse.json(posts);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const post = await db.post.create({ data: body });
  return NextResponse.json(post, { status: 201 });
}
```

## Anti-Patterns to Avoid

❌ **Using Client Components unnecessarily**
```tsx
"use client"; // Don't add this unless you need interactivity!
export function StaticContent() {
  return <div>Hello</div>;
}
```

❌ **Fetching in Client Components when Server Components work**
```tsx
"use client";
export function Posts() {
  const [posts, setPosts] = useState([]);
  useEffect(() => {
    fetch('/api/posts').then(r => r.json()).then(setPosts);
  }, []);
  // Should be Server Component with async/await!
}
```

❌ **Not using TypeScript**
```tsx
export function Component({ data }) { // No types!
  return <div>{data.name}</div>;
}
```

❌ **Mixing styling approaches inconsistently**
```tsx
// Don't mix Tailwind and CSS Modules randomly
<div className="flex" style={{ color: 'red' }}>
  <span className={styles.text}>Mixed styles</span>
</div>
```

❌ **Not optimizing images**
```tsx
<img src="/large-image.jpg" /> // Use next/image instead!
```

## Quick Reference

### File Conventions
- `layout.tsx` - Shared UI for segments
- `page.tsx` - Unique UI for route
- `loading.tsx` - Loading UI with Suspense
- `error.tsx` - Error UI boundary
- `not-found.tsx` - 404 UI
- `route.ts` - API endpoint
- `template.tsx` - Re-rendered layout

### Component Checklist
- [ ] Use Server Component by default
- [ ] Add `"use client"` only if needed
- [ ] Define TypeScript interfaces
- [ ] Handle loading states
- [ ] Handle error states
- [ ] Add proper ARIA labels
- [ ] Optimize images with next/image
- [ ] Test responsive design
- [ ] Check performance with Lighthouse

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Images optimized
- [ ] Metadata/SEO configured
- [ ] Error tracking setup
- [ ] Analytics integrated
- [ ] Performance tested
- [ ] Accessibility tested

---

This skill provides the foundation for building modern Next.js 16 applications. Apply these patterns consistently, prioritize Server Components, and focus on creating exceptional user experiences.
