/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-06
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : composant objet de formulaire modal pour modifier un jeu de plateforme.
 */
import { Component } from "react";

/**
 * Fenetre modale de modification d'un jeu existant.
 */
class EditGameDialog extends Component {
  /**
   * Initialise l'etat local du formulaire de modification.
   *
   * @param {Object} props - Proprietes React du composant.
   * @returns {void} L'etat du formulaire est initialise.
   */
  constructor(props) {
    super(props);
    this.state = { form: this.buildForm(props.game) };
  }

  /**
   * Resynchronise le formulaire quand un autre jeu est ouvert.
   *
   * @param {Object} previousProps - Anciennes proprietes React.
   * @returns {void} Met a jour l'etat local si necessaire.
   */
  componentDidUpdate(previousProps) {
    if (previousProps.game !== this.props.game) {
      this.setState({ form: this.buildForm(this.props.game) });
    }
  }

  /**
   * Construit le formulaire a partir d'un jeu.
   *
   * @param {Object|null} game - Jeu selectionne pour modification.
   * @returns {Object} Donnees de formulaire normalisees.
   */
  buildForm(game) {
    const source = game || {};
    return {
      "Nom du jeu": source["Nom du jeu"] || "",
      Studio: source.Studio || "",
      "Date de sortie": source["Date de sortie"] || "",
      "Date d'achat": source["Date d'achat"] || "",
      "Lieu d'achat": source["Lieu d'achat"] || "",
      Note: source.Note || "",
      "Prix d'achat": source["Prix d'achat"] ?? "",
      Version: source.Version || "",
    };
  }

  /**
   * Met a jour un champ du formulaire.
   *
   * @param {string} field - Nom du champ modifie.
   * @param {string} value - Nouvelle valeur du champ.
   * @returns {void} Met a jour l'etat local.
   */
  updateField(field, value) {
    this.setState((previous) => ({ form: { ...previous.form, [field]: value } }));
  }

  /**
   * Soumet les valeurs modifiees au parent.
   *
   * @param {SubmitEvent} event - Evenement de soumission du formulaire.
   * @returns {void} Transmet le formulaire au callback parent.
   */
  submit(event) {
    event.preventDefault();
    this.props.onSubmit(this.props.game, this.state.form);
  }

  /**
   * Rend un champ texte simple.
   *
   * @param {string} field - Nom du champ.
   * @param {string} type - Type HTML de l'input.
   * @param {boolean} required - Indique si le champ est obligatoire.
   * @returns {import("react").JSX.Element} Champ de formulaire.
   */
  renderInput(field, type = "text", required = false) {
    return (
      <label>
        {field}
        <input
          type={type}
          min={type === "number" ? "0" : undefined}
          step={type === "number" ? "0.01" : undefined}
          value={this.state.form[field]}
          onChange={(event) => this.updateField(field, event.target.value)}
          required={required}
        />
      </label>
    );
  }

  /**
   * Rend la modale complete de modification.
   *
   * @param {void} Aucun - Utilise les props et l'etat React.
   * @returns {import("react").JSX.Element|null} Modale ou rien si aucun jeu n'est selectionne.
   */
  render() {
    if (!this.props.game) {
      return null;
    }

    return (
      <div className="modalOverlay" role="presentation">
        <section className="editGameDialog" role="dialog" aria-modal="true">
          <header className="editGameDialogHeader">
            <div>
              <p className="eyebrow">Modification</p>
              <h2>{this.props.game["Nom du jeu"]}</h2>
            </div>
            <button type="button" className="secondaryButton" onClick={this.props.onCancel}>
              Fermer
            </button>
          </header>
          <form className="addGameForm" onSubmit={(event) => this.submit(event)}>
            {this.renderInput("Nom du jeu", "text", true)}
            {this.renderInput("Studio")}
            {this.renderInput("Date de sortie", "date")}
            {this.renderInput("Date d'achat", "date", true)}
            {this.renderInput("Lieu d'achat", "text", true)}
            {this.renderInput("Note")}
            {this.renderInput("Prix d'achat", "number", true)}
            {this.renderInput("Version")}
            <div className="formActions">
              <button type="button" className="secondaryButton" onClick={this.props.onCancel}>
                Annuler
              </button>
              <button type="submit" disabled={this.props.isSaving}>
                {this.props.isSaving ? "Modification..." : "Modifier le jeu"}
              </button>
            </div>
          </form>
        </section>
      </div>
    );
  }
}

export default EditGameDialog;
