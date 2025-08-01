import React, { useState } from 'react';
import ShortenerForm from '../components/ShortenerForm';
import ShortenedList from '../components/ShortenedList';

function URLShortenerPage() {
  const [shortened, setShortened] = useState([]);
  return (
    <>
      <ShortenerForm onShortened={setShortened} />
      <ShortenedList items={shortened} />
    </>
  );
}

export default URLShortenerPage;
