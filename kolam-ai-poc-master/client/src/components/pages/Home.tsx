import { useMutation } from "@tanstack/react-query"
import api from "../../lib/axios/axios"
import { API_ROUTES } from "../../lib/api"
import { useRef, useState } from "react";
import { JsonViewer } from "../ui/home/JsonViewer";

export default function Home() {

  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [history, setHistory] = useState<{
    knowYourKolam: string;
    searchKolam: string[];
    predictKolam: string;
  }[] | null>(null);
  const [renderHistory, setRenderHistory] = useState<string[] | null>(null);
  const [jsonInput, setJsonInput] = useState<string>("");


  const knowYourKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.KNOW_YOUR_KOLAM,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data;
    }
  });

  const searchKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.SEARCH,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data.matches;
    }
  });

  const predictKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.PREDICT,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data.prediction;
    }
  });

  const renderKolamMuation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post(
        API_ROUTES.KOLAM.RENDER,
        data, // send parsed object directly
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return res.data.file;
    },
    onSuccess: (data) => {
      setRenderHistory(prev => ([...(prev || []), data]));
    }
  });

  const handleAnalyze = async () => {
    if (!file) return;

    try {
      const [knowResult, searchResult, predictResult] = await Promise.all([
        knowYourKolamMutation.mutateAsync(file),
        searchKolamMutation.mutateAsync(file),
        predictKolamMutation.mutateAsync(file)
      ]);

      // update history only after all mutations are complete
      setHistory(prev => ([
        ...(prev || []),
        {
          knowYourKolam: JSON.stringify(knowResult),
          searchKolam: searchResult,
          predictKolam: predictResult,
        }
      ]));

      // clean up UI state
      setFile(null);
      setPreview(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (error) {
      console.error('Error analyzing kolam:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPreview(URL.createObjectURL(file));
      setFile(file);
    }
  };

  return (
    <div className="grid grid-cols-5 h-full w-full">
      {/* main content */}
      <div className="col-span-4 p-8 w-full h-full bg-gray-50 h-screen overflow-y-auto">
        <div className="flex flex-col gap-8 h-full">
          {/* {predictKolamMutation.data && searchKolamMutation.data && (
            <MessageBox width="fit-content" text={`Hmm, I think it's from the ${predictKolamMutation.data}, it's well known as ${predictKolamMutation.data == "Maharastra" ? "Rangoli" : "Kolam"} in ${predictKolamMutation.data}.\nHere are some similar kolams I found in our database:`}>
              <div className="grid grid-cols-3 gap-4">
                {searchKolamMutation.data.map((imgstr: string) => (
                  <div key={imgstr} className="h-[200px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                    <img
                      src={imgstr.startsWith('http') ? imgstr : `${import.meta.env.VITE_API_URL}/${imgstr}`}
                      alt="Similar kolam"
                      className="object-cover w-full h-full"
                    />
                  </div>
                ))}
              </div>
            </MessageBox>
          )}
          {knowYourKolamMutation.data && (
            <MessageBox width="fit-content" text={`Here's a Mathematical representation of your kolam (in JSON format) \nYou can copy and generate using our kolam renderer API`}>
              <JsonViewer text={JSON.stringify(knowYourKolamMutation.data)} />
            </MessageBox>
          )} */}
          {
            (!history || history.length < 1) && (!renderHistory || renderHistory.length < 1) && (
              <div className="w-full h-full bg-white rounded-2xl p-4 flex items-center justify-center flex-col">
                <img src="/logo.webp" alt="" />
                <p className="text-gray-500">Upload a kolam image to get started</p>
              </div>
            )
          }
          {
            history && history.length > 0 && history.map((item, _index) => (
              <>
                <MessageBox width="fit-content" text={`Hmm, I think it's from the ${item.predictKolam}, it's well known as ${item.predictKolam == "Maharastra" ? "Rangoli" : "Kolam"} in ${item.predictKolam}.\nHere are some similar kolams I found in our database:`}>
                  <div className="grid grid-cols-3 gap-4">
                    {item.searchKolam.map((imgstr: string) => (
                      <div key={imgstr} className="h-[200px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                        <img
                          src={imgstr.startsWith('http') ? imgstr : `${import.meta.env.VITE_API_URL}/${imgstr}`}
                          alt="Similar kolam"
                          className="object-cover w-full h-full"
                        />
                      </div>
                    ))}
                  </div>
                </MessageBox>
                <MessageBox width="fit-content" text={`Here's a Mathematical representation of your kolam (in JSON format) \nYou can copy and generate using our kolam renderer API`}>
                  <JsonViewer text={item.knowYourKolam} />
                </MessageBox>
              </>
            ))
          }
          {
            renderHistory && renderHistory.length > 0 && renderHistory.map((imgstr: string, _index) => (
              <MessageBox key={imgstr} width="fit-content" text={`Here's the kolam rendered from your JSON input`}>
                <div className="h-[300px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                  <object
                    type="image/svg+xml"
                    data={imgstr.startsWith("http") ? imgstr : `${import.meta.env.VITE_API_URL}/${imgstr}`}
                    className="w-full h-full"
                  />
                </div>
              </MessageBox>
            ))
          }
        </div>
      </div>
      {/* sidebar */}
      <div className="col-span-1 border-l border-gray-200 p-5">
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        <div
          className="w-full aspect-square flex flex-col items-center justify-center border-2 border-dashed border-gray-400 rounded-2xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition overflow-hidden"
          onClick={() => inputRef.current?.click()}
        >
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="object-cover w-full h-full"
            />
          ) : (
            <>
              <span className="text-4xl text-gray-500">+</span>
              <p className="text-gray-600 mt-2">Upload Photo</p>
            </>
          )}
        </div>
        {
          file ? (
            <button
              className="px-4 py-2 text-primary border-1 font-semibold border-primary rounded-lg mt-4 bg-white"
              onClick={handleAnalyze}
              disabled={knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending}
            >
              {(knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending) ? "Analyzing kolam..." : "Analyze"}
            </button>
          ) : null
        }
        <textarea
          className="w-full border border-gray-300 rounded-lg p-4 mt-8 resize-none text-xs"
          placeholder="Add json to render kolam.."
          rows={10}
          onChange={(e) => setJsonInput(e.target.value)}
        ></textarea>

        {jsonInput.trim().length > 0 ? (
          <button
            className="px-4 py-2 text-primary border-1 font-semibold border-primary rounded-lg mt-4 bg-white"
            onClick={() => {
              try {
                const parsed = JSON.parse(jsonInput); // must be object with dots + paths
                renderKolamMuation.mutate(parsed);
              } catch {
                alert("Invalid JSON");
              }
            }}
            disabled={renderKolamMuation.isPending}
          >
            Render Kolam
          </button>
        ) : null}
      </div>
    </div>
  )
}

function MessageBox({ width, children, text }: { width: string, children?: React.ReactNode, text?: string }) {
  return (
    <div className={`bg-white p-4 rounded-lg shadow flex gap-2 justify-start items-start`} style={{ maxWidth: width }}>
      <div className="min-w-10 min-h-10 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
        <img src="/logo.webp" alt="logo" className="object-cover w-10 h-10" />
      </div>
      <div className="mt-1 flex flex-col gap-6 mr-4">
        {text && <div className="text-gray-800 whitespace-pre-wrap">{text}</div>}
        {
          children ? children : <p className="text-gray-800">Hello, how can I help you?</p>
        }
      </div>
    </div>
  )
}