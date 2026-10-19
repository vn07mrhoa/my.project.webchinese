const { createApp, ref, computed, onMounted, nextTick } = Vue;

createApp({
  setup() {
    // Navigation
    const activeTab = ref('search'); // 'search', 'stroke', 'review', 'quiz', 'notebook'
    const toastMessage = ref('');
    
    // Stats
    const stats = ref({
      total_words: 0,
      notebook_count: 0,
      mastered_count: 0,
      total_quizzes: 0,
      avg_score: 0
    });

    // --- TAB 1: SEARCH STATE ---
    const searchQuery = ref('');
    const searchResults = ref([]);
    const selectedWord = ref(null);
    const activeHskTab = ref(1);
    const hskWords = ref([]);
    let searchTimeout = null;

    // --- TAB 2: STROKE & HANZI WRITER STATE ---
    const strokeInput = ref('好');
    const currentChar = ref('好');
    const strokeCharacters = ref(['好']);
    const showOutline = ref(true);
    const strokeFeedback = ref('');
    const strokeFeedbackSuccess = ref(false);
    let hanziWriterInstance = null;

    // --- TAB 3: FLASHCARDS & SRS STATE ---
    const flashcards = ref([]);
    const currentCardIndex = ref(0);
    const isCardFlipped = ref(false);
    const flashcardFilter = ref('due');
    const dueCardsCount = computed(() => flashcards.value.length);
    const currentCard = computed(() => flashcards.value[currentCardIndex.value] || {});

    // --- TAB 4: QUIZ STATE ---
    const quizzes = ref([]);
    const currentQuizIndex = ref(0);
    const selectedAnswerIndex = ref(null);
    const quizScore = ref(0);
    const quizCompleted = ref(false);
    const quizLevel = ref(0); // 0: Tất cả cấp độ
    const quizDifficulty = ref('all'); // 'all', 'easy', 'medium', 'hard'
    const quizType = ref('all');
    const quizAnswersHistory = ref([]);
    const reorderUserTokens = ref([]);
    const reorderAvailableTokens = ref([]);
    const currentQuiz = computed(() => quizzes.value[currentQuizIndex.value] || {});

    // --- TAB 5: NOTEBOOK STATE ---
    const notebookItems = ref([]);

    // --- TAB 6: TOPIC / LESSONS STATE ---
    const topics = ref([]);
    const selectedTopic = ref(null);
    const topicSubTab = ref('vocab'); // 'vocab', 'dialogue', 'grammar', 'quiz'
    const topicQuizAnswers = ref({});
    const frequentVocabs = computed(() => {
      if (!selectedTopic.value || !selectedTopic.value.vocabularies) return [];
      return selectedTopic.value.vocabularies.filter(v => v.is_frequent);
    });

    // --- NOTIFICATION HELPER ---
    const showToast = (msg) => {
      toastMessage.value = msg;
      setTimeout(() => {
        toastMessage.value = '';
      }, 3000);
    };

    // --- AUDIO SPEECH SYNTHESIS ---
    const speak = (text) => {
      if (!text) return;
      if (!('speechSynthesis' in window)) {
        showToast('Trình duyệt không hỗ trợ phát âm tự động');
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance.rate = 0.85; // Tốc độ vừa phải cho người học
      
      // Tìm giọng tiếng Trung nếu có
      const voices = window.speechSynthesis.getVoices();
      const zhVoice = voices.find(v => v.lang.includes('zh') || v.lang.includes('cmn'));
      if (zhVoice) {
        utterance.voice = zhVoice;
      }

      window.speechSynthesis.speak(utterance);
    };

    // --- BADGE COLOR HELPER ---
    const hskBadgeClass = (lvl) => {
      const classes = {
        1: 'bg-emerald-100 text-emerald-800',
        2: 'bg-teal-100 text-teal-800',
        3: 'bg-sky-100 text-sky-800',
        4: 'bg-indigo-100 text-indigo-800',
        5: 'bg-purple-100 text-purple-800',
        6: 'bg-rose-100 text-rose-800',
      };
      return classes[lvl] || 'bg-slate-100 text-slate-800';
    };

    // --- API CALLS: STATS ---
    const loadStats = async () => {
      try {
        const res = await fetch('/api/stats');
        stats.value = await res.json();
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    };

    // --- SEARCH METHODS ---
    const handleSearchInput = () => {
      if (searchTimeout) clearTimeout(searchTimeout);
      if (!searchQuery.value.trim()) {
        searchResults.value = [];
        return;
      }
      searchTimeout = setTimeout(() => {
        performSearch();
      }, 300);
    };

    const performSearch = async () => {
      if (!searchQuery.value.trim()) return;
      selectedWord.value = null;
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(searchQuery.value.trim())}`);
        const data = await res.json();
        searchResults.value = data.data || [];
        if (searchResults.value.length === 1) {
          selectWord(searchResults.value[0]);
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    };

    const selectWord = (word) => {
      selectedWord.value = word;
      window.scrollTo({ top: 180, behavior: 'smooth' });
    };

    const loadHskWords = async (level) => {
      activeHskTab.value = level;
      try {
        const res = await fetch(`/api/hsk/${level}`);
        const data = await res.json();
        hskWords.value = data.data || [];
      } catch (err) {
        console.error('Error fetching HSK words:', err);
      }
    };

    // --- HANZI WRITER & STROKE METHODS ---
    const openStrokeTab = (chineseStr) => {
      strokeInput.value = chineseStr;
      activeTab.value = 'stroke';
      nextTick(() => {
        initStrokeWriter();
      });
    };

    const initStrokeWriter = () => {
      const targetChar = strokeInput.value.trim();
      if (!targetChar) return;

      // Chia nhỏ chuỗi thành mảng các ký tự
      const chars = Array.from(targetChar).filter(c => /[\u4e00-\u9fa5]/.test(c));
      if (chars.length === 0) {
        showToast('Vui lòng nhập chữ Hán hợp lệ');
        return;
      }

      strokeCharacters.value = chars;
      selectCharForStroke(chars[0]);
    };

    const selectCharForStroke = (char) => {
      currentChar.value = char;
      strokeFeedback.value = '';
      strokeFeedbackSuccess.value = false;

      const container = document.getElementById('character-target');
      if (!container) return;
      container.innerHTML = '';

      if (typeof HanziWriter === 'undefined') {
        console.error('HanziWriter library not loaded yet');
        return;
      }

      const size = window.innerWidth < 640 ? 260 : 300;

      hanziWriterInstance = HanziWriter.create('character-target', char, {
        width: size,
        height: size,
        padding: 12,
        strokeColor: '#dc2626',
        radicalColor: '#16a34a',
        outlineColor: '#fca5a5',
        showOutline: showOutline.value,
        showCharacter: true,
        strokeAnimationSpeed: 1.2,
        delayBetweenStrokes: 150
      });

      // Tự động chạy animation mẫu 1 lần
      hanziWriterInstance.animateCharacter();
    };

    const animateStroke = () => {
      if (!hanziWriterInstance) return;
      strokeFeedback.value = 'Đang vẽ nét mẫu theo bút thuận...';
      strokeFeedbackSuccess.value = false;
      hanziWriterInstance.showCharacter();
      hanziWriterInstance.animateCharacter({
        onComplete: () => {
          strokeFeedback.value = 'Hoàn thành xem nét mẫu!';
          strokeFeedbackSuccess.value = true;
        }
      });
    };

    const startQuizWriting = () => {
      if (!hanziWriterInstance) return;
      strokeFeedback.value = 'Hãy dùng chuột hoặc tay đồ theo nét chữ!';
      strokeFeedbackSuccess.value = false;
      hanziWriterInstance.quiz({
        onMistake: (strokeData) => {
          strokeFeedback.value = `Sai nét thứ ${strokeData.strokeNum + 1}! Hãy thử lại theo quy tắc.`;
          strokeFeedbackSuccess.value = false;
        },
        onCorrectStroke: (strokeData) => {
          strokeFeedback.value = `Đúng nét ${strokeData.strokeNum + 1}/${strokeData.totalStrokes}! Rất tốt!`;
          strokeFeedbackSuccess.value = true;
        },
        onComplete: (summaryData) => {
          strokeFeedback.value = `Tuyệt vời! Bạn đã viết đúng chữ "${currentChar.value}"! 🎉`;
          strokeFeedbackSuccess.value = true;
          // Pháo hoa ăn mừng
          if (typeof confetti === 'function') {
            confetti({
              particleCount: 80,
              spread: 60,
              origin: { y: 0.7 }
            });
          }
        }
      });
    };

    const resetWriter = () => {
      if (!currentChar.value) return;
      selectCharForStroke(currentChar.value);
    };

    const toggleOutline = () => {
      showOutline.value = !showOutline.value;
      if (hanziWriterInstance) {
        if (showOutline.value) {
          hanziWriterInstance.showOutline();
        } else {
          hanziWriterInstance.hideOutline();
        }
      }
    };

    // --- FLASHCARD METHODS (SRS) ---
    const loadFlashcards = async () => {
      try {
        const res = await fetch(`/api/flashcards?filter=${flashcardFilter.value}`);
        const data = await res.json();
        flashcards.value = data.data || [];
        currentCardIndex.value = 0;
        isCardFlipped.value = false;
      } catch (err) {
        console.error('Error loading flashcards:', err);
      }
    };

    const rateFlashcard = async (rating) => {
      const card = currentCard.value;
      if (!card || !card.word_id) return;

      try {
        await fetch(`/api/flashcards/${card.word_id}/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ rating })
        });

        // Next card with smooth flip reset
        isCardFlipped.value = false;
        setTimeout(() => {
          currentCardIndex.value++;
          loadStats();
          if (currentCardIndex.value >= flashcards.value.length && typeof confetti === 'function') {
            confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
          }
        }, 150);

      } catch (err) {
        console.error('Error submitting review:', err);
      }
    };

    // --- QUIZ & EXERCISES METHODS ---
    const loadQuizzes = async () => {
      quizCompleted.value = false;
      currentQuizIndex.value = 0;
      quizScore.value = 0;
      selectedAnswerIndex.value = null;
      quizAnswersHistory.value = [];

      try {
        const url = `/api/quizzes?level=${quizLevel.value}&type=${quizType.value}&difficulty=${quizDifficulty.value}&count=20`;
        const res = await fetch(url);
        const data = await res.json();
        quizzes.value = data.data || [];
        setupCurrentQuestion();
      } catch (err) {
        console.error('Error loading quizzes:', err);
      }
    };

    const setupCurrentQuestion = () => {
      selectedAnswerIndex.value = null;
      reorderUserTokens.value = [];
      const q = currentQuiz.value;
      if (q && q.type === 'reorder' && q.extra_data && q.extra_data.tokens) {
        reorderAvailableTokens.value = [...q.extra_data.tokens];
      } else {
        reorderAvailableTokens.value = [];
      }
    };

    const addTokenToReorder = (token, idx) => {
      if (selectedAnswerIndex.value !== null) return;
      reorderUserTokens.value.push(token);
      reorderAvailableTokens.value.splice(idx, 1);
    };

    const removeTokenFromReorder = (token, idx) => {
      if (selectedAnswerIndex.value !== null) return;
      reorderUserTokens.value.splice(idx, 1);
      reorderAvailableTokens.value.push(token);
    };

    const submitReorderAnswer = () => {
      if (selectedAnswerIndex.value !== null) return;
      const q = currentQuiz.value;
      if (!q || !q.extra_data || !q.extra_data.correct_order) return;
      const userSentence = reorderUserTokens.value.join('');
      const correctSentence = q.extra_data.correct_order.join('');
      const isCorrect = userSentence === correctSentence;
      selectedAnswerIndex.value = isCorrect ? 0 : 1;
      if (isCorrect) {
        quizScore.value++;
      }
      quizAnswersHistory.value.push({
        question_id: q.id,
        user_choice: userSentence,
        correct_choice: correctSentence,
        is_correct: isCorrect
      });
    };

    const formatQuizType = (t) => {
      const map = {
        'reorder': '🧩 Sắp xếp câu hoàn chỉnh',
        'cloze': '✏️ Điền từ vào chỗ trống',
        'true_false': '⚖️ Nhận định Đúng / Sai',
        'listening': '🎧 Luyện nghe phát âm',
        'meaning': '🔠 Nghĩa của từ',
        'pinyin': '📝 Phiên âm Pinyin',
        'hanzi': '🈴 Nhận diện chữ Hán',
        'all': '🎯 Đề tổng hợp đa dạng'
      };
      return map[t] || 'Bài tập';
    };

    const formatDifficulty = (d) => {
      const map = {
        'easy': '🟢 Mức độ Dễ',
        'medium': '🟡 Mức độ Trung bình',
        'hard': '🔴 Mức độ Nâng cao'
      };
      return map[d] || 'Cơ bản';
    };

    const submitQuizAnswer = (optIdx) => {
      if (selectedAnswerIndex.value !== null) return; // Prevent multiple clicks
      selectedAnswerIndex.value = optIdx;
      
      const q = currentQuiz.value;
      const isCorrect = optIdx === q.correct_index;
      if (isCorrect) {
        quizScore.value++;
      }

      quizAnswersHistory.value.push({
        question_id: q.id,
        user_choice: optIdx,
        correct_choice: q.correct_index,
        is_correct: isCorrect
      });
    };

    const nextQuiz = () => {
      if (currentQuizIndex.value + 1 < quizzes.value.length) {
        currentQuizIndex.value++;
        setupCurrentQuestion();
      } else {
        finishQuiz();
      }
    };

    const finishQuiz = async () => {
      quizCompleted.value = true;
      if (quizScore.value / quizzes.value.length >= 0.7 && typeof confetti === 'function') {
        confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
      }

      try {
        await fetch('/api/quizzes/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            level: quizLevel.value,
            quiz_type: quizType.value,
            score: quizScore.value,
            total: quizzes.value.length,
            details: quizAnswersHistory.value
          })
        });
        loadStats();
      } catch (err) {
        console.error('Error saving quiz result:', err);
      }
    };

    const getOptionButtonClass = (optIdx) => {
      if (selectedAnswerIndex.value === null) {
        return 'border-slate-200 hover:border-red-400 hover:bg-red-50/40 text-slate-800';
      }
      if (optIdx === currentQuiz.value.correct_index) {
        return 'border-emerald-500 bg-emerald-50 text-emerald-900 font-bold';
      }
      if (optIdx === selectedAnswerIndex.value) {
        return 'border-rose-500 bg-rose-50 text-rose-900';
      }
      return 'border-slate-200 text-slate-400 opacity-60';
    };

    const getOptionBadgeClass = (optIdx) => {
      if (selectedAnswerIndex.value === null) {
        return 'bg-slate-100 text-slate-700';
      }
      if (optIdx === currentQuiz.value.correct_index) {
        return 'bg-emerald-600 text-white';
      }
      if (optIdx === selectedAnswerIndex.value) {
        return 'bg-rose-600 text-white';
      }
      return 'bg-slate-100 text-slate-400';
    };

    // --- NOTEBOOK METHODS ---
    const loadNotebook = async () => {
      try {
        const res = await fetch('/api/notebook');
        const data = await res.json();
        notebookItems.value = data.data || [];
        loadStats();
      } catch (err) {
        console.error('Error loading notebook:', err);
      }
    };

    const toggleNotebook = async (word) => {
      if (!word) return;
      if (word.is_favorited) {
        await removeNotebookItem(word.id);
        word.is_favorited = 0;
      } else {
        try {
          await fetch(`/api/notebook/${word.id}`, { method: 'POST' });
          word.is_favorited = 1;
          showToast(`Đã thêm "${word.simplified}" vào sổ tay & chu kỳ ôn tập!`);
          loadStats();
        } catch (err) {
          console.error('Error adding to notebook:', err);
        }
      }
    };

    const removeNotebookItem = async (wordId) => {
      try {
        await fetch(`/api/notebook/${wordId}`, { method: 'DELETE' });
        showToast('Đã xóa khỏi sổ tay');
        if (selectedWord.value && selectedWord.value.id === wordId) {
          selectedWord.value.is_favorited = 0;
        }
        loadNotebook();
      } catch (err) {
        console.error('Error removing notebook item:', err);
      }
    };

    // --- TOPIC / LESSONS METHODS ---
    const loadTopics = async () => {
      try {
        const res = await fetch('/api/topics');
        const data = await res.json();
        topics.value = data.data || [];
      } catch (err) {
        console.error('Error loading topics:', err);
      }
    };

    const openTopic = async (topic) => {
      if (topic.is_locked) {
        showToast('Bài này chưa đăng ký! Bấm "Mở khóa học thử" để học ngay.');
        return;
      }
      try {
        const res = await fetch(`/api/topics/${topic.id}`);
        const data = await res.json();
        selectedTopic.value = data;
        topicSubTab.value = 'vocab';
        topicQuizAnswers.value = {};
        window.scrollTo({ top: 120, behavior: 'smooth' });
      } catch (err) {
        console.error('Error fetching topic detail:', err);
      }
    };

    const unlockTopic = (topic) => {
      topic.is_locked = 0;
      showToast(`Đã mở khóa "${topic.title}"! Chúc bạn học tốt.`);
      openTopic(topic);
    };

    const playFullDialogue = () => {
      if (!selectedTopic.value || !selectedTopic.value.dialogues) return;
      const dlgs = selectedTopic.value.dialogues;
      let idx = 0;
      
      const speakNext = () => {
        if (idx >= dlgs.length) return;
        const line = dlgs[idx];
        const utterance = new SpeechSynthesisUtterance(line.zh);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.85;
        utterance.onend = () => {
          idx++;
          setTimeout(speakNext, 400);
        };
        window.speechSynthesis.speak(utterance);
      };

      window.speechSynthesis.cancel();
      speakNext();
    };

    const quickSaveNotebook = async (vocab) => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(vocab.simplified)}`);
        const searchData = await res.json();
        if (searchData.data && searchData.data.length > 0) {
          const word = searchData.data[0];
          await fetch(`/api/notebook/${word.id}`, { method: 'POST' });
          showToast(`Đã lưu "${vocab.simplified}" vào sổ tay!`);
          loadStats();
        } else {
          showToast(`Đã đánh dấu từ "${vocab.simplified}"!`);
        }
      } catch (err) {
        console.error('Quick save notebook error:', err);
      }
    };

    const answerTopicQuiz = (qIdx, optIdx, correctIdx) => {
      if (topicQuizAnswers.value[qIdx] !== undefined) return;
      topicQuizAnswers.value[qIdx] = optIdx;
      if (optIdx === correctIdx) {
        if (typeof confetti === 'function') {
          confetti({ particleCount: 50, spread: 50, origin: { y: 0.7 } });
        }
      }
    };

    const getTopicQuizOptClass = (qIdx, optIdx, correctIdx) => {
      const userChoice = topicQuizAnswers.value[qIdx];
      if (userChoice === undefined) {
        return 'border-slate-200 hover:border-red-400 hover:bg-red-50/30 text-slate-800';
      }
      if (optIdx === correctIdx) {
        return 'border-emerald-500 bg-emerald-50 text-emerald-900 font-bold';
      }
      if (optIdx === userChoice) {
        return 'border-rose-500 bg-rose-50 text-rose-900';
      }
      return 'border-slate-200 text-slate-400 opacity-60';
    };

    onMounted(() => {
      loadStats();
      loadHskWords(1);
      loadTopics();
      // Khởi tạo tab Luyện viết sẵn sàng
      setTimeout(() => {
        initStrokeWriter();
      }, 500);
    });

    return {
      activeTab,
      toastMessage,
      stats,
      searchQuery,
      searchResults,
      selectedWord,
      activeHskTab,
      hskWords,
      strokeInput,
      currentChar,
      strokeCharacters,
      showOutline,
      strokeFeedback,
      strokeFeedbackSuccess,
      flashcards,
      currentCardIndex,
      isCardFlipped,
      flashcardFilter,
      dueCardsCount,
      currentCard,
      quizzes,
      currentQuizIndex,
      selectedAnswerIndex,
      quizScore,
      quizCompleted,
      quizLevel,
      quizType,
      currentQuiz,
      notebookItems,
      hskBadgeClass,
      handleSearchInput,
      performSearch,
      selectWord,
      loadHskWords,
      speak,
      openStrokeTab,
      initStrokeWriter,
      selectCharForStroke,
      animateStroke,
      startQuizWriting,
      resetWriter,
      toggleOutline,
      loadFlashcards,
      rateFlashcard,
      loadQuizzes,
      formatQuizType,
      submitQuizAnswer,
      nextQuiz,
      getOptionButtonClass,
      getOptionBadgeClass,
      loadNotebook,
      toggleNotebook,
      removeNotebookItem,
      topics,
      selectedTopic,
      topicSubTab,
      topicQuizAnswers,
      loadTopics,
      openTopic,
      unlockTopic,
      playFullDialogue,
      quickSaveNotebook,
      answerTopicQuiz,
      getTopicQuizOptClass,
      frequentVocabs,
      quizDifficulty,
      formatDifficulty,
      reorderUserTokens,
      reorderAvailableTokens,
      addTokenToReorder,
      removeTokenFromReorder,
      submitReorderAnswer
    };
  }
}).mount('#app');
