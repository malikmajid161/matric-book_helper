import type {Metadata} from 'next';
import './globals.css';
import 'katex/dist/katex.min.css';
export const metadata: Metadata = {title: 'PTB Scholar · Your study companion', description: 'Read Punjab class 10 textbooks, practice exercises, and learn with textbook-grounded AI.'};
export default function Layout({children}: Readonly<{children: React.ReactNode}>) {
  return <html lang="en" suppressHydrationWarning><body>{children}</body></html>;
}
