"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface Query {
  id: string;
  query: string;
  response: string;
  resolved: boolean;
  created_at: string;
}

export default function QueriesPage() {
  const [queries, setQueries] = useState<Query[]>([]);
  const [answer, setAnswer] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolved, setResolved] = useState<Query[]>([]);

  const fetchQueries = async () => {
    try {
      const response = await fetch("http://localhost:8000/queries?status=UNRESOLVED");
      if (!response.ok) throw new Error("Failed to fetch queries");
      const data = await response.json();
      setQueries(data);
    } catch (err) {
      setError("Error fetching queries");
    } finally {
      setLoading(false);
    }
  };
  const fetchResolvedQueries = async () => {
    try {
      const response = await fetch("http://localhost:8000/queries?status=RESOLVED");
      if (!response.ok) throw new Error("Failed to fetch resolved queries");
      const data = await response.json();
      setResolved(data);
    } catch (err) {
      setError("Error fetching resolved queries");
    }
  };

  // Fetch unresolved queries
  useEffect(() => {
    Promise.all([fetchQueries(), fetchResolvedQueries()]);
  }, []);

  // Handle resolve action
  const handleResolve = async (queryId: string) => {
    if (!answer[queryId]) {
      alert("Please provide an answer before resolving");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/queries/${queryId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: answer[queryId] }),
      });
      if (!response.ok) throw new Error("Failed to resolve query");
      setQueries(queries.filter((q) => q.id !== queryId));
      setAnswer((prev) => {
        const newAnswers = { ...prev };
        delete newAnswers[queryId];
        return newAnswers;
      });
      fetchResolvedQueries();
    } catch (err) {
      alert("Error resolving query");
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;
  if (error) return <div className="text-center py-10 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold mb-6">Unresolved Queries</h1>
        <Link href="/">HOME</Link>
      </div>

      {queries.length === 0 ? (
        <p className="text-gray-500 text-center my-5">No unresolved queries found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">ID</th>
                <th className="py-2 px-4 border-b">Question</th>
                <th className="py-2 px-4 border-b">Answer</th>
                <th className="py-2 px-4 border-b">Action</th>
              </tr>
            </thead>
            <tbody>
              {queries.map((query) => (
                <tr key={query.id}>
                  <td className="py-2 px-4 border-b">{query.id}</td>
                  <td className="py-2 px-4 border-b">{query.query}</td>
                  <td className="py-2 px-4 border-b">
                    <textarea
                      className="w-full p-2 border rounded"
                      placeholder="Enter answer..."
                      value={answer[query.id] || ""}
                      onChange={(e) => setAnswer({ ...answer, [query.id]: e.target.value })}
                    />
                  </td>
                  <td className="py-2 px-4 border-b">
                    <button
                      onClick={() => handleResolve(query.id)}
                      className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                    >
                      Resolve
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="overflow-x-auto">
        <div>
          <h1>All Resolved Query</h1>
        </div>
        <table className="min-w-full bg-white border">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">User ID</th>
              <th className="py-2 px-4 border-b">Question</th>
              <th className="py-2 px-4 border-b">Answer</th>
              <th className="py-2 px-4 border-b">Action</th>
            </tr>
          </thead>
          <tbody>
            {resolved.map((query) => (
              <tr key={query.id}>
                <td className="py-2 px-4 border-b">{query.id}</td>
                <td className="py-2 px-4 border-b">{query.query}</td>
                <td className="py-2 px-4 border-b">
                  <p>{query.response}</p>
                </td>
                <td className="py-2 px-4 border-b text-center text-green-600">Resolved</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
