"use client";

import { useState } from 'react';

interface ScrapeResult {
  title: string;
  price: number | string;
  url: string;
  source: string;
}

export default function HomePage() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState<ScrapeResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'An unknown error occurred.');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-24 bg-gray-50">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          商品価格チェッカー
        </h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-8 bg-white rounded-lg shadow-md">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="メルカリの商品ページのURLを貼り付け"
            required
            className="p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="p-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {isLoading ? '取得中...' : '価格を取得'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-100 text-red-700 border border-red-300 rounded-md">
            <p><span className="font-bold">エラー:</span> {error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6 p-4 bg-green-100 border border-green-300 rounded-md shadow-sm">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">取得結果</h2>
            <div className="space-y-2">
              <p><strong>タイトル:</strong> {result.title}</p>
              <p><strong>価格:</strong> &yen;{typeof result.price === 'number' ? result.price.toLocaleString() : result.price}</p>
              <p><strong>ソース:</strong> <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{result.source}</a></p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
