import { useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { Bookmark, BookmarkFilled } from './Icons';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { bookmarkService } from '../lib/services';

export function BookmarkButton({ kind, id, bookmarked = false }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState(Boolean(bookmarked));

  useEffect(() => {
    setSaved(Boolean(bookmarked));
  }, [bookmarked]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (kind === 'media') {
        const { data } = await bookmarkService.toggleMedia(id);
        return data;
      }
      const { data } = await bookmarkService.toggleArticle(id);
      return data;
    },
    onSuccess: (data) => {
      setSaved(Boolean(data.bookmarked));
      toast.success(data.bookmarked ? t('saved.added') : t('saved.removed'));
      queryClient.invalidateQueries({ queryKey: queryKeys.bookmarks() });
      if (kind === 'media') {
        queryClient.invalidateQueries({ queryKey: queryKeys.mediaItem(id) });
      } else {
        queryClient.invalidateQueries({ queryKey: queryKeys.article(id) });
      }
    },
    onError: (err) => {
      toast.error(extractError(err));
    },
  });

  if (!user || !id) return null;

  return (
    <button
      type="button"
      className="btn-secondary inline-flex items-center gap-2 text-sm"
      aria-pressed={saved}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {saved ? <BookmarkFilled className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
      {saved ? t('saved.bookmarked') : t('saved.bookmark')}
    </button>
  );
}
