const getPageNumbers = (numberOfPosts: number, reqtotalPages: number) => {
  const numberOfPages = numberOfPosts / Number(reqtotalPages);

  let pageNumbers: number[] = [];
  for (let i = 1; i <= Math.ceil(numberOfPages); i++) {
    pageNumbers = [...pageNumbers, i];
  }

  return pageNumbers;
};

export default getPageNumbers;
