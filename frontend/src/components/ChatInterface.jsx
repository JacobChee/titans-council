import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Stage1 from './Stage1';
import Stage2 from './Stage2';
import Stage3 from './Stage3';
import './ChatInterface.css';

const TITANS = [
  { emoji: '⚡', name: 'Elon Musk' },
  { emoji: '🍎', name: 'Steve Jobs' },
  { emoji: '📦', name: 'Jeff Bezos' },
  { emoji: '💪', name: 'Alex Hormozi' },
  { emoji: '🟢', name: 'Jensen Huang' },
];

const EXAMPLES = [
  'Should I start a business or get a high-paying job?',
  'How do I price my product or service?',
  'What is the most important thing to focus on in the first year of a startup?',
  'How do I know when to quit something?',
];

const STAGE_LABELS = {
  stage1: '⚡ Titans are thinking...',
  stage2: '🔁 Titans are ranking each other...',
  stage3: '🏛️ Synthesising final answer...',
};

export default function ChatInterface({ conversation, onSendMessage, isLoading, onBack }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleExample = (example) => {
    if (!isLoading) {
      onSendMessage(example);
    }
  };

  const showLanding = !conversation || conversation.messages.length === 0;

  return (
    <div className="chat-interface">

      {showLanding ? (
        <div className="landing">
          <div className="landing-icon">🏛️</div>
          <div className="landing-title">Titans Council</div>
          <p className="landing-tagline">
            Ask any hard question. Five of the world's greatest business minds answer — each in their own voice — then debate and synthesise a final verdict.
          </p>

          <div className="landing-how">
            <div className="landing-step">
              <div className="landing-step-num">Step 1</div>
              <div className="landing-step-text">You ask a question</div>
            </div>
            <div className="landing-step">
              <div className="landing-step-num">Step 2</div>
              <div className="landing-step-text">Each titan answers in their own style</div>
            </div>
            <div className="landing-step">
              <div className="landing-step-num">Step 3</div>
              <div className="landing-step-text">They rank each other's answers</div>
            </div>
            <div className="landing-step">
              <div className="landing-step-num">Step 4</div>
              <div className="landing-step-text">One synthesised final answer</div>
            </div>
          </div>

          <div className="landing-titans">
            {TITANS.map(t => (
              <div key={t.name} className="landing-titan-chip">
                <span>{t.emoji}</span>
                <span>{t.name}</span>
              </div>
            ))}
          </div>

          <div className="landing-examples">
            <div className="landing-examples-label">Try asking</div>
            {EXAMPLES.map(ex => (
              <div key={ex} className="landing-example" onClick={() => handleExample(ex)}>
                {ex}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
        <div className="chat-header">
          <button className="back-btn" onClick={onBack}>← Home</button>
        </div>
        <div className="messages-container">
          {conversation.messages.map((msg, index) => (
            <div key={index} className="message-group">
              {msg.role === 'user' ? (
                <div className="user-message">
                  <div className="user-bubble">{msg.content}</div>
                </div>
              ) : (
                <div className="assistant-message">
                  <div className="assistant-label">🏛️ Titans Council</div>

                  {msg.loading?.stage1 && (
                    <div className="stage-loading">
                      <div className="spinner" />
                      <span>{STAGE_LABELS.stage1}</span>
                    </div>
                  )}
                  {msg.stage1 && <Stage1 responses={msg.stage1} />}

                  {msg.loading?.stage2 && (
                    <div className="stage-loading">
                      <div className="spinner" />
                      <span>{STAGE_LABELS.stage2}</span>
                    </div>
                  )}
                  {msg.stage2 && (
                    <Stage2
                      rankings={msg.stage2}
                      labelToModel={msg.metadata?.label_to_model}
                      aggregateRankings={msg.metadata?.aggregate_rankings}
                    />
                  )}

                  {msg.loading?.stage3 && (
                    <div className="stage-loading">
                      <div className="spinner" />
                      <span>{STAGE_LABELS.stage3}</span>
                    </div>
                  )}
                  {msg.stage3 && <Stage3 finalResponse={msg.stage3} />}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        </>
      )}

      <div className="input-area">
        <form className="input-form" onSubmit={handleSubmit}>
          <textarea
            className="message-input"
            placeholder="Ask the Titans anything... (Enter to send, Shift+Enter for new line)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={2}
          />
          <button type="submit" className="send-button" disabled={!input.trim() || isLoading}>
            {isLoading ? '...' : 'Ask →'}
          </button>
        </form>
        <div className="input-hint">Powered by Elon · Jobs · Bezos · Hormozi · Jensen</div>
      </div>

    </div>
  );
}
