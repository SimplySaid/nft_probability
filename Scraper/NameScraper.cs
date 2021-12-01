using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Observer;
using Observer.Models;
using Solnet.Rpc;
using Solnet.Rpc.Models;
using Solnet.Wallet.Utilities;

namespace Scraper
{
    /// <summary>
    /// Implements a scraper to create datasets of metadata information for NFT collections.
    /// </summary>
    public class NameScraper : ScraperBase
    {
        /// <summary>
        /// Initialize the name scraper.
        /// </summary>
        /// <param name="client">The rpc client instance.</param>
        /// <param name="logger">The logger instance.</param>
        /// <param name="name">The name to search for.</param>
        /// <param name="separator">The separator for the non-fungible token id.</param>
        public NameScraper(IRpcClient client, ILogger logger, string name, string symbol, string address, string separator) : base(client, logger,
            name, symbol, address, separator)
        {
            _name = name;
            _symbol = symbol;
            _address = address;
            _sep = separator;
        }

        /// <summary>
        /// Run the scraper to build datasets of metadata.
        /// </summary>
        public async Task Run()
        {
            _logger.LogInformation($"[{_name}] Loading metadata accounts for {_name}.");
            // 69 is the offset of the name in the metadata account
            var metadataAccounts = await GetMetadataAccounts(_name, _symbol);
            _metadataAccountWrappers = new List<MetadataAccountWrapper>();
            foreach (var metadataAccount in metadataAccounts)
            {
                //Console.WriteLine(Encoders.Base58.EncodeData(Encoding.UTF8.GetBytes(metadataAccount.ToString())));

                var metadata =
                    MetadataAccount.Deserialize(Convert.FromBase64String(metadataAccount.Account.Data[0]));
                
                
                
                /*_logger.LogInformation($"Decoded Data Account: {metadataAccount.PublicKey}\t" +
                                       $"- Mint: {metadata.Mint}\t" +
                                       $"- Name: {metadata.Data.Name}\t" +
                                       $"- Symbol: {metadata.Data.Symbol}\t" +
                                       $"- Uri: {metadata.Data.Uri}");
                                       */

                metadata.Data.Name = metadata.Data.Name.Trim('\0');
                metadata.Data.Symbol = metadata.Data.Symbol.Trim('\0');
                metadata.Data.Uri = metadata.Data.Uri.Trim('\0');
                if (string.IsNullOrWhiteSpace(metadata.Data.Uri)) continue;

                var idSplit = metadata.Data.Name.Split(_sep);
                int id = -1;
                if (idSplit.Length >= 2)
                {
                    idSplit[1] = new string(idSplit[1].TakeWhile(c => Char.IsDigit(c)).ToArray());
                    var success = int.TryParse(idSplit[1], out id);
                    if (!success)
                    {
                        // This is because of names that have information after the id
                        idSplit = idSplit[1].Split(" ");
                        if (idSplit.Length != 0)
                            int.TryParse(idSplit[0], out id);
                    }
                }

                var imageUrlSplit = metadata.Data.Uri.Split(".net/");
                string imageUrl = "";
                if (imageUrlSplit.Length == 2) imageUrl = imageUrlSplit[1];
                _metadataAccountWrappers.Add(new MetadataAccountWrapper
                {
                    Address = metadataAccount.PublicKey,
                    Metadata = metadata,
                    Id = id,
                    Image = imageUrl,
                    Mint = metadata.Mint,
                    Name = metadata.Data.Name,
                    Symbol = metadata.Data.Symbol,
                    ArweaveUri = metadata.Data.Uri
                });
            }

            await File.WriteAllTextAsync($"{_name.Replace(" ", "")}-metadata.json",
                JsonSerializer.Serialize(_metadataAccountWrappers, _jsonSerializerOptions));

            _logger.LogInformation(
                $"[{_name}] Finished loading {_metadataAccountWrappers.Count} metadata accounts for {_name}, loading arweave.");
            var metadataWrappers = _metadataAccountWrappers.Where(item => item.ArweaveUri != null).ToList();
            var newWrappers = new List<MetadataAccountWrapper>();
            var i = 1;
            foreach (var item in metadataWrappers)
            {
                var processedItem = await GetArweaveData(item, _address);
                if (processedItem == null) continue;
                processedItem.Mint = item.Mint;
                processedItem.Address = item.Address;
                processedItem.ArweaveUri = item.ArweaveUri;
                newWrappers.Add(processedItem);
                _logger.LogInformation(
                    $"[{_name}] [{i}/{metadataWrappers.Count}] Loaded arweave data for {item.Name} - {item.Id}.");
                i++;
            }

            _logger.LogInformation($"[{_name}] Finished loading arweave data, writing to file.");
            await File.WriteAllTextAsync($"{_name.Replace(" ", "")}.json",
                JsonSerializer.Serialize(newWrappers.Where(x => x != null).ToList(), _jsonSerializerOptions));

            _logger.LogInformation($"[{_name}] Finished writing metadata accounts for {_name} to file");
        }
    }
}