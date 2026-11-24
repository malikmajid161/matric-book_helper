export type Topic = {id: string; title: string; page_number: number; key_points?: string[]};
export type Exercise = {id: string; text: string; page_number: number};
export type Chapter = {number: number; title: string; start_page: number; end_page?: number; topics: Topic[]; exercises: Exercise[]; pages?: {page_number: number; text: string}[]};
export type Book = {id: string; title: string; edition: string; status: string; bytes: number; sha256: string; version?: string; chapters: Chapter[]};
export type Bundle = Pick<Book, 'id' | 'title' | 'edition' | 'sha256' | 'chapters'> & {version: string};
export type CachedBook = {bundle: Bundle; pdf: Blob; savedAt: number};
export type Source = {id: string; book: string; chapter_number: number; chapter_title: string; page_number: number; text: string; citation: number; distance: number;page_text?:string;verification?:string;book_title?:string};
export type Answer = {answer: string; supported: boolean; sources: Source[]};
