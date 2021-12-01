using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Console;
using Solnet.Rpc;

namespace Scraper
{
    class Program
    {
        /// <summary>
        /// The rpc client instance.
        /// </summary>
        private static IRpcClient _rpcClient;
        
        /// <summary>
        /// The names of the collections to get and the separator of their number.
        /// </summary>
        private static Dictionary<string, Tuple<string, string, string>> _collections = new()
        {
            ///{"Lunaria", Tuple.Create("LUN", "#")},
            ///{"Eternal Beings", Tuple.Create("EBeings", "#")},
            ///{"Red Panda", Tuple.Create("REDPANDA", "#")},
            ///{ "Galactic Gecko", Tuple.Create("GGSG", "#") },
            ///{"3D SOLDIER", Tuple.Create("", "8tKpJSKcwnPKCyxSpWQm4JeNfY76kWZkbiZcYExzsTvd", "#")},
            ///{"2D SOLDIER", Tuple.Create("", "8tKpJSKcwnPKCyxSpWQm4JeNfY76kWZkbiZcYExzsTvd", "#") },
            ///{ "PixelDix", Tuple.Create("", "DSmbnj9t7CCQdAZfvYe3PNbJB7CrVXpa29iW3VkgpEEZ", "#") },
            ///{ "Boneworld", Tuple.Create("BW", "7TKTuN4bGAV3LuRqA7rtC8QHVA34FAKCb8RDKdvaau99", "#")},
            ///{ "Solfinity", Tuple.Create("SFTY", "4ADxHQZmugBbZSr3YFB6XmNgEfYV1Pd63FBkUdbhjwhL", "#") },
            ///{ "Mech", Tuple.Create("MECH", "5VNbPYPh9UBcS5PwjHM8obcsz9bs5pVBRYA7nG96WHE7", "#") },
            ///{ "Galactic Gecko", Tuple.Create("GGSG", "B5MPcaEGNF3iZH5kLjPPfhy3ieXbQ8Cgb77zSZD6gNSn", "#") },
            ///{ "Scene", Tuple.Create("Infinity", "CH8QmtwGwzy9BAJi14poz12XVxtKEpAke1tPTkMFBuuC", "#") },
            ///{ "Scene", Tuple.Create("Infinity", "CH8QmtwGwzy9BAJi14poz12XVxtKEpAke1tPTkMFBuuC", "#") },
            ///{ "", Tuple.Create("WEAPONS", "7gbxCxJkWcop1FCoaHnB6JJaRjpnkMxJFNbqtTS8KJbD", "#") },
            ///{ "Meerkat", Tuple.Create("Meerkat", "FLARQdNnEz8qzGD5oS67eZbSmY94dqx5RheRXJmHjsaX", "#") },
            ///{ "ShellRacer", Tuple.Create("TSR", "7aHtZ1genuVeMFZ4GtDDdKz54nU6o9Sn2zwias46WEoV", "#") },
            ///{ "Gloom Punk", Tuple.Create("GLOOM", "3jGJHMaCMcz9miRJAHL7sPrkqDXLH3k1Rj8PNBAeimai", "#") },
            ///{ "FAB PUNK", Tuple.Create("", "CUpfayqaoQjyNTrGUfkWspet1X1DmV8YuSY9pvGbAdMY", "#") },
            ///{ "", Tuple.Create("", "54d4aHuAw9XrYSxvtPJMLcBqgoUyq9a2Y4tE1GfdtS2A", "#") },
            ///{ "SolCities", Tuple.Create("SCG", "B7D1hSkGcC5DwAL2xrBuuhs7GujcoHGTcZgPgyYH7vdp", "#") },
            ///{ "DCBear", Tuple.Create("", "2KY1uPptiu15dA3fXE8PU5qJ7T85MNbqLvwWozNXKkhD", "#") },
            ///{ "", Tuple.Create("Solagon IO", "2mpExMNeGaHaGeq369fdzbQE42jQwfTJ3mExXCMrAz6y", "") },
            ///{ "Solameleon", Tuple.Create("Solameleon", "3ktoq644v5x3k2jBiNRPwbg5vwwcrgK3SA5HAEFD5yeC", "#") },
            ///{ "Corrupt Catz", Tuple.Create("CCATZ", "6q5DrEmwVRWQe9Xcr2tyrToFvpwg5iU1Fsk1rDnwQPmZ", "#") },
            ///{ "", Tuple.Create("KAM1", "EdX5kdnmdwdUpRqQh8zdmvmf3dUaVxBWPwUaezgvsonf", "#") },
            ///{"Cyber Pharmacist", Tuple.Create("CPHARM", "4K6evwuydiR9WhfRBb6c3GrGMRjKzkDu1n8rTKf16amy", "") },
            ///{ "SEALZ", Tuple.Create("SEAL", "6g8oEzmPYn7mHt5AdWqRBqj142FjDWxWSH9rM2dZRcdE", "#") },
            ///{ "solchicks", Tuple.Create("SOLCHICKS", "H5ZQGeTv23nJRcFmEprRLuM9cTeJMajYvf2k1JhuLhE2", "") },
            ///{ "Unirexcity", Tuple.Create("UNIREX", "2is2NRunEwhotCQrRFXt2w3Fy2Vdo6pasiWzJK4HpcQU", "") },
            ///{ "SKYLINE", Tuple.Create("SKY", "2is2NRunEwhotCQrRFXt2w3Fy2Vdo6pasiWzJK4HpcQU", "#") },
            { "Cyber Technician", Tuple.Create("CTECH", "2is2NRunEwhotCQrRFXt2w3Fy2Vdo6pasiWzJK4HpcQU", "#") },










            ///{ "Waifu", Tuple.Create("WDAO", "#") },
            ///{ "SolChan", Tuple.Create("", "HyfWtQjKwoP9wRxFfceVq1ptqpJHCrM9qWXS5ieFgh9t", "#") }

            /*{"Bold Badger", "#"}
            { "SolPunk", "#" },
            { "Degen Ape", "#"}, 
            { "Solanimal", "#" },
            { "SolMee", "#"},
            { "THUG", "#" },
            { "Top Hat Chicks", "#" },
            { "Solstones", ""},
            { "Nogoalfaces", ""},
            { "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "#"},
            { "BOOGLE", "#" },
            { "SSBxSolPunk", "Punk_#" },
            { "Abstraction", "No."},
            { "Frakt", "-"},           
            { "SolanaDoge", "#" },
            { "Sollamas", "#" },
            { "SMB", "#"}*/
        };

        private static void Main(string[] args)
        {
            ILogger _logger = null;
#if DEBUG
            _logger = GetDebugLogger();
#elif RELEASE
            _logger = GetInformationLogger();
#endif
            _rpcClient = ClientFactory.GetClient(Cluster.MainNet);
            
            _logger.LogInformation($"Launching scrapers.");

            foreach (var collection in _collections)
            {
                if (collection.Key == "SMB")
                {
                     var symbolScraper = new SymbolScraper(
                         _rpcClient, 
                         _logger,
                         collection.Key,
                         collection.Value.Item1,
                         collection.Value.Item2,
                         collection.Value.Item3);
                     Task.Run(() => symbolScraper.Run());
                     continue;
                }
                var nameScraper = new NameScraper(
                    _rpcClient, 
                    _logger,
                    collection.Key,
                    collection.Value.Item1,
                    collection.Value.Item2,
                    collection.Value.Item3);
                Task.Run(() => nameScraper.Run());
            }
            
            _logger.LogInformation("Finished scraping metadata.");
            Console.ReadKey();
        }
        
        private static ILogger GetInformationLogger()
        {
            return LoggerFactory.Create(x =>
            {
                x.AddSimpleConsole(o =>
                    {
                        o.UseUtcTimestamp = true;
                        o.IncludeScopes = true;
                        o.ColorBehavior = LoggerColorBehavior.Enabled;
                        o.TimestampFormat = "HH:mm:ss ";
                    })
                    .SetMinimumLevel(LogLevel.Information);
            }).CreateLogger<NameScraper>();
        }

        private static ILogger GetDebugLogger()
        {
            return LoggerFactory.Create(x =>
            {
                x.AddSimpleConsole(o =>
                    {
                        o.UseUtcTimestamp = true;
                        o.IncludeScopes = true;
                        o.ColorBehavior = LoggerColorBehavior.Enabled;
                        o.TimestampFormat = "HH:mm:ss ";
                    })
                    .SetMinimumLevel(LogLevel.Debug);
            }).CreateLogger<NameScraper>();
        }
    }
}