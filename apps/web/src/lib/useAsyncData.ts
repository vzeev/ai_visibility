import { useCallback, useEffect, useState } from "react";

export type AsyncState<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
  reload: () => Promise<void>;
};

export function useAsyncData<T>(load: () => Promise<T>, dependencies: unknown[] = []): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setData(await load());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Request failed");
    } finally {
      setIsLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, error, isLoading, reload };
}
