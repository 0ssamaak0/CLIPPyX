using System.IO;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using ManagedCommon;
using Microsoft.PowerToys.Settings.UI.Library;
using Wox.Plugin;
using Wox.Plugin.Logger;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Text.Json;
using System.Collections.Immutable;

namespace Community.PowerToys.Run.Plugin.CLIPPyX
{


    /// <summary>
    /// Main class of this plugin that implement all used interfaces.
    /// </summary>
    public class Main : IPlugin, IContextMenu, IDisposable, ISettingProvider
    {

        const string UrlClipText = "http://localhost:23107/clip_text";
        const string UrlClipImage = "http://localhost:23107/clip_image";
        const string UrlEmbedText = "http://localhost:23107/ebmed_text";


        private CancellationTokenSource _cancellationTokenSource;
        private readonly int _debounceTime = 500; // 500ms debounce time
        private readonly object _lock = new object();


        /// <summary>
        /// ID of the plugin.
        /// </summary>
        public static string PluginID => "AE953C974C2241878F282EA18A7769E4";

        /// <summary>
        /// Name of the plugin.
        /// </summary>
        public string Name => "CLIPPyX";

        static public double ThresholdEmbedText { get; set; }
        static public int TopKEmbedText { get; set; }
        static public double ThresholdClipImage { get; set; }
        static public int TopKClipImage { get; set; }
        static public double ThresholdClipText { get; set; }
        static public int TopKClipText { get; set; }

        /// <summary>
        /// Description of the plugin.
        /// </summary>
        public string Description => "CLIPPyX provides an OS-wide image search that supports semantic search in both image content and text on images";


        public static List<string> GetEmbedText(string query)
        {
            return GetClipResult(UrlEmbedText, query, ThresholdEmbedText, TopKEmbedText);
        }
        public static List<string> GetClipImage(string query)
        {
            if(!query.StartsWith(@"https://") && !query.StartsWith(@"http://")){
                query=query.Replace(@"\", @"\\");
            }
            query=query.Replace("\"", "\\\"");

            return GetClipResult(UrlClipImage, query, ThresholdClipImage, TopKClipImage);
        }

        public static List<string> GetClipText(string query)
        {
            return GetClipResult(UrlClipText, query, ThresholdClipText, TopKClipText);
        }
        private static List<string> GetClipResult(string url, string query, double threshold, int topK)
        {
            HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
            webRequest.AllowAutoRedirect = true;
            webRequest.ContentType = "application/json";
            webRequest.Method = "POST";
            
            string content = $"{{\"query\": \"{query}\", \"threshold\": {threshold}, \"top_k\": {topK}}}";
            ASCIIEncoding encoding = new ASCIIEncoding();
            byte[] contentBytes = encoding.GetBytes(content);
            webRequest.ContentLength = contentBytes.Length;

            Stream newStream = webRequest.GetRequestStream();
            newStream.Write(contentBytes, 0, contentBytes.Length);
            newStream.Close();

            HttpWebResponse webResponse = (HttpWebResponse)webRequest.GetResponse();
            StreamReader readContent = new StreamReader(webResponse.GetResponseStream());
            string responseText = readContent.ReadToEnd();
            webResponse.Close();

            var res = JsonSerializer.Deserialize<List<string>>(responseText);
            return res ?? new List<string>();
        }

        /// <summary>
        /// Additional options for the plugin.
        /// </summary>
        public IEnumerable<PluginAdditionalOption> AdditionalOptions => [
            new()
            {
                Key = nameof(ThresholdClipText),
                DisplayLabel = "Threshold for Clip Text",
                DisplayDescription = "Double: Threshold for the similarity search.",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=ThresholdClipText,
                NumberBoxMin=0,
                NumberBoxMax=1
            },
            new()
            {
                Key = nameof(TopKClipText),
                DisplayLabel = "Max number of results for Clip Text",
                DisplayDescription = "Integer: Max number of results",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=TopKClipText,
                NumberBoxMin=1,
            },
            new()
            {
                Key = nameof(ThresholdClipImage),
                DisplayLabel = "Threshold for Clip Image",
                DisplayDescription = "Double: Threshold for the similarity search.",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=ThresholdClipImage,
                NumberBoxMin=0,
                NumberBoxMax=1
            },
            new()
            {
                Key = nameof(TopKClipImage),
                DisplayLabel = "Max number of results for Clip Image",
                DisplayDescription = "Integer: Max number of results",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=TopKClipImage,
                NumberBoxMin=1,
            },
            new()
            {
                Key = nameof(ThresholdEmbedText),
                DisplayLabel = "Threshold for Embed Text",
                DisplayDescription = "Double: Threshold for the similarity search.",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=ThresholdEmbedText,
                NumberBoxMin=0,
                NumberBoxMax=1
            },
            new()
            {
                Key = nameof(TopKEmbedText),
                DisplayLabel = "Max number of results for Embed Text",
                DisplayDescription = "Integer: Max number of results",
                PluginOptionType = PluginAdditionalOption.AdditionalOptionType.Numberbox,
                NumberValue=TopKEmbedText,
                NumberBoxMin=1,
            },
        ];


        private PluginInitContext? Context { get; set; }

        private string? IconPath { get; set; }

        private bool Disposed { get; set; }


        /// <summary>
        /// Initialize the plugin with the given <see cref="PluginInitContext"/>.
        /// </summary>
        /// <param name="context">The <see cref="PluginInitContext"/> for this plugin.</param>
        public void Init(PluginInitContext context)
        {
            Log.Info("Init", GetType());

            Context = context ?? throw new ArgumentNullException(nameof(context));
            Context.API.ThemeChanged += OnThemeChanged;
            if (TopKClipImage == 0)
            {
                TopKClipImage = 1;
            }
            if (TopKClipText == 0)
            {
                TopKClipText = 1;
            }
            if (TopKEmbedText == 0)
            {
                TopKEmbedText = 1;
            }
            UpdateIconPath(Context.API.GetCurrentTheme());
            _cancellationTokenSource = new CancellationTokenSource();
        }

        /// <summary>
        /// Return a list context menu entries for a given <see cref="Result"/> (shown at the right side of the result).
        /// </summary>
        /// <param name="selectedResult">The <see cref="Result"/> for the list with context menu entries.</param>
        /// <returns>A list context menu entries.</returns>
        public List<ContextMenuResult> LoadContextMenus(Result selectedResult)
        {
            Log.Info("LoadContextMenus", GetType());

            return
            [
                new ContextMenuResult
                    {
                        PluginName = Name,
                        Title = "Open File Location (Enter)",
                        FontFamily = "Segoe Fluent Icons,Segoe MDL2 Assets",
                        Glyph = "\xE838", // Copy
                        Action = _ => OpenFolder(selectedResult.SubTitle),
                    },
                ];

        }

        /// <summary>
        /// Creates setting panel.
        /// </summary>
        /// <returns>The control.</returns>
        /// <exception cref="NotImplementedException">method is not implemented.</exception>
        public Control CreateSettingPanel() => throw new NotImplementedException();

        /// <summary>
        /// Updates settings.
        /// </summary>
        /// <param name="settings">The plugin settings.</param>
        public void UpdateSettings(PowerLauncherPluginSettings settings)
        {
            Log.Info("UpdateSettings", GetType());

            ThresholdClipImage = settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(ThresholdClipImage))?.NumberValue ?? 0.0;
            TopKClipImage = (int)(settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(TopKClipImage))?.NumberValue ?? 3);
            ThresholdClipText = settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(ThresholdClipText))?.NumberValue ?? 0.0;
            TopKClipText = (int)(settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(TopKClipText))?.NumberValue ?? 3);
            ThresholdEmbedText = settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(ThresholdEmbedText))?.NumberValue ?? 0.0;
            TopKEmbedText = (int)(settings.AdditionalOptions.SingleOrDefault(x => x.Key == nameof(TopKEmbedText))?.NumberValue ?? 3);

        }

        /// <inheritdoc/>
        public void Dispose()
        {
            Log.Info("Dispose", GetType());

            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Wrapper method for <see cref="Dispose()"/> that dispose additional objects and events form the plugin itself.
        /// </summary>
        /// <param name="disposing">Indicate that the plugin is disposed.</param>
        protected virtual void Dispose(bool disposing)
        {
            Context.API.SaveAppAllSettings();
            if (Disposed || !disposing)
            {
                return;
            }

            if (Context?.API != null)
            {
                Context.API.ThemeChanged -= OnThemeChanged;
            }

            Disposed = true;
        }

        private void UpdateIconPath(Theme theme) => IconPath = theme == Theme.Light || theme == Theme.HighContrastWhite ? Context?.CurrentPluginMetadata.IcoPathLight : Context?.CurrentPluginMetadata.IcoPathDark;

        private void OnThemeChanged(Theme currentTheme, Theme newTheme) => UpdateIconPath(newTheme);


        private static bool OpenFolder(string path)
        {
            try
            {
                path=path.Replace(@"/", @"\");
                string argument = $"/select,\"{path}\"";

                
                Process.Start("explorer.exe", argument);
            }
            catch (Exception e)
            {
                Log.Error(e.Message, typeof(Main));
                return false;
            }
            return true;
        }
        private static bool OpenFile(string path)
        {
            try
            {
                path=path.Replace(@"/", @"\");
                Process.Start("explorer.exe", $"\"{path}\"");
            }
            catch (Exception e)
            {
                Log.Error(e.Message, typeof(Main));
                return false;
            }
            return true;
        }

        public List<Result> Query(Query query)
        {
            ArgumentNullException.ThrowIfNull(query);

            Log.Info("Query: " + query.Search, GetType());

            // Cancel any previous pending operation
            lock (_lock)
            {
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource = new CancellationTokenSource();
            }

            try
            {
                // Wait for the debounce period
                Task.Delay(_debounceTime, _cancellationTokenSource.Token).Wait();

                // If we get here without being canceled, execute the query
                return ExecuteQuery(query);
            }
            catch (TaskCanceledException)
            {
                // The task was canceled, so we return an empty list
                return new List<Result>();
            }
            catch (AggregateException ae)
            {
                if (ae.InnerExceptions.Any(e => e is TaskCanceledException))
                {
                    // The task was canceled, so we return an empty list
                    return new List<Result>();
                }
                // If it's not a TaskCanceledException, rethrow
                throw;
            }
        }

        private List<Result> ExecuteQuery(Query query)
        {
            try
            {
                string querySearch = query.Search.Trim();
                if (querySearch.Length == 0)
                    return new List<Result>
                    {
                        new Result
                        {
                            Title = "Empty Query",
                            SubTitle = "CLIPPyX",
                            IcoPath = Context?.CurrentPluginMetadata.IcoPathLight,
                        },
                    };
                List<string> responses = new List<string>();

                if (querySearch.StartsWith('|'))
                {
                    string queryKeyword = querySearch.Substring(1).Trim();
                    responses = GetEmbedText(queryKeyword);
                }
                else if (querySearch.StartsWith('#'))
                {
                    string queryKeyword = querySearch.Substring(1).Trim();
                    responses = GetClipImage(queryKeyword);
                }
                else
                {
                    responses = GetClipText(querySearch);
                }

                if (responses.Count == 0)
                {
                    return new List<Result>
                {
                    new Result
                    {
                        Title = "No results found",
                        SubTitle = "CLIPPyX",
                        IcoPath = Context?.CurrentPluginMetadata.IcoPathLight,
                    },
                };
                }

                return responses.Select(response => new Result
                {
                    Title = new FileInfo(response).Name,
                    SubTitle = response,
                    IcoPath = response,
                    Action = _ => OpenFile(response),
                }).ToList();
            }
            catch (Exception e)
            {
                return new List<Result>
            {
                new Result
                {
                    Title = "Please make sure server is running and configured correctly",
                    SubTitle = "Error",
                    IcoPath = Context?.CurrentPluginMetadata.IcoPathLight,
                },
            };
            }
        }

    }
}
