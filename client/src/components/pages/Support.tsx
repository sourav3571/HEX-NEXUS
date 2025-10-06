import { useState } from "react";

export default function Support() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    issue: "",
    message: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Thank you for your feedback! We'll get back to you soon.");
    setFormData({ name: "", email: "", issue: "", message: "" });
  };

  const faqs = [
    { question: "How to search Kolam designs by state?", answer: "Go to the Learn page and select the state buttons at the top to view designs from that state." },
    { question: "How to download Kolam designs?", answer: "Click on any design image to open it in full size, then right-click and select 'Save image as...'." },
    { question: "Can I upload my own designs?", answer: "Currently, uploads are not supported, but stay tuned for future updates!" },
  ];

  return (
    <div className="p-8 space-y-10">
      <h1 className="text-3xl font-bold">Support & Help</h1>

      {/* FAQ Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Frequently Asked Questions</h2>
        <div className="space-y-2">
          {faqs.map((faq, index) => (
            <details key={index} className="border rounded p-2">
              <summary className="font-medium cursor-pointer">{faq.question}</summary>
              <p className="mt-2 text-gray-700">{faq.answer}</p>
            </details>
          ))}
        </div>
      </div>

      {/* Feedback Form */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Send us a message</h2>
        <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Your Name"
            className="w-full p-2 border rounded"
            required
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Your Email"
            className="w-full p-2 border rounded"
            required
          />
          <select
            name="issue"
            value={formData.issue}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          >
            <option value="">Select Issue Type</option>
            <option value="Bug">Bug</option>
            <option value="Suggestion">Suggestion</option>
            <option value="Feedback">Feedback</option>
          </select>
          <textarea
            name="message"
            value={formData.message}
            onChange={handleChange}
            placeholder="Describe your issue..."
            className="w-full p-2 border rounded"
            rows={4}
            required
          />
          <button type="submit" className="bg-primary text-white px-4 py-2 rounded">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}
