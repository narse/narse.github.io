import getPageNumbers from "./getPageNumbers";

interface GetPaginationProps<T> {
  posts: T;
  page: string | number;
  isIndex?: boolean;
  reqtotalPages: number;
}

const getPagination = <T>({
  posts,
  page,
  reqtotalPages,
  isIndex = false,
}: GetPaginationProps<T[]>) => {
  const totalPagesArray = getPageNumbers(posts.length, reqtotalPages);
  const totalPages = totalPagesArray.length;

  const currentPage = isIndex
    ? 1
    : page && !isNaN(Number(page)) && totalPagesArray.includes(Number(page))
      ? Number(page)
      : 0;

  const lastPost = isIndex ? reqtotalPages : currentPage * reqtotalPages;
  const startPost = isIndex ? 0 : lastPost - reqtotalPages;
  const paginatedPosts = posts.slice(startPost, lastPost);

  return {
    totalPages,
    currentPage,
    paginatedPosts,
  };
};

export default getPagination;
