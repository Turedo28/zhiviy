import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const pathname = request.nextUrl.pathname;

  // Public routes (dashboard is public in demo mode)
  const publicRoutes = ['/', '/api', '/dashboard'];

  // Check if route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // Redirect to home if no token and trying to access protected route
  if (!token && !isPublicRoute && pathname !== '/') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // Redirect to dashboard if logged in and trying to access home
  if (token && pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
